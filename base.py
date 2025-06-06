import itertools
import operator
import os

from collections import namedtuple
from . import data


def write_tree (directory='.'):
    entries = []
    with os.scandir (directory) as it:
        for entry in it:
            full = f'{directory}/{entry.name}'
            if is_ignored (full):
                continue

            if entry.is_file (follow_symlinks=False):
                type_ = 'blob'
                with open (full, 'rb') as f:
                    oid = data.hash_object (f.read ())
            elif entry.is_dir (follow_symlinks=False):
                type_ = 'tree'
                oid = write_tree (full)
            entries.append ((entry.name, oid, type_))

    tree = ''.join (f'{type_} {oid} {name}\n'
                    for name, oid, type_
                    in sorted (entries))
    return data.hash_object (tree.encode (), 'tree')


#Ağaç nesnesi içindeki girdileri okur ve yield ile birer birer dışarı verir.
def _iter_tree_entries (oid):
    if not oid:
        return
    tree = data.get_object (oid, 'tree')
    for entry in tree.decode ().splitlines ():
        type_, oid, name = entry.split (' ', 2)
        yield type_, oid, name

#Ağaç yapısını düz bir sözlük haline getirir (path → blob oid)
def get_tree (oid, base_path=''):
    result = {}
    for type_, oid, name in _iter_tree_entries (oid):
        assert '/' not in name
        assert name not in ('..', '.')
        path = base_path + name
        if type_ == 'blob':
            result[path] = oid
        elif type_ == 'tree':
            result.update (get_tree (oid, f'{path}/'))
        else:
            assert False, f'Unknown tree entry {type_}'
    return result


def _empty_current_directory ():
    for root, dirnames, filenames in os.walk ('.', topdown=False):
        for filename in filenames:
            path = os.path.relpath (f'{root}/{filename}')
            if is_ignored (path) or not os.path.isfile (path):
                continue
            os.remove (path)
        for dirname in dirnames:
            path = os.path.relpath (f'{root}/{dirname}')
            if is_ignored (path):
                continue
            try:
                os.rmdir (path)
            except (FileNotFoundError, OSError):
                # Deletion might fail if the directory contains ignored files,
                # so it's OK
                pass

#Bu sözlüğü kullanarak gerçek dosya sistemine dosyaları yazar.
def read_tree (tree_oid):
    _empty_current_directory ()
    for path, oid in get_tree (tree_oid, base_path='./').items ():
        os.makedirs (os.path.dirname (path), exist_ok=True)
        with open (path, 'wb') as f:
            f.write (data.get_object (oid))


# tree 29109329e9012921091290219
# author co
# time 2025 bla bla

# this is the commit message!    

# we will create a new ugit commit command that will accept a commit message,
# snapshot the current directory using ugitwrite-tree and save the resulting object.


def commit(message):
    commit = f'tree {write_tree()}\n'

    HEAD = data.get_HEAD()
    if HEAD:
        commit += f'parent {HEAD}\n'

    commit += '\n'  
    commit += f'{message}\n'

    oid = data.hash_object (commit.encode (), 'commit')

    data.set_HEAD (oid)

    return oid


def checkout(oid):
    commit = get_commit(oid)
    read_tree(commit.tree)
    data.set_HEAD(oid)


Commit = namedtuple("Commit",["tree", "parent", "message"])


def get_commit(oid):
    parent = None

    commit = data.get_object(oid,"commit").decode()
    lines = iter(commit.splitlines())
    for line in itertools.takewhile(operator.truth, lines):
        key, value = line.split(" ", 1)
        if key == "tree":
            tree = value
        elif key == "parent":
            parent = value
        else:
            assert False, f"Unknown field {key}"

    message = '\n'.join(lines)
    return Commit(tree=tree, parent=parent, message=message)


def is_ignored (path):
    return '.ugit' in path.split ('/')




