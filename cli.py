import argparse
import os
import sys
import textwrap

from . import base
from . import data

def main():
    args = parse_args()
    args.func(args)

def parse_args():        #  Komut satırı argümanlarını ayrıştırmak için yardımcı fonksiyon.
    parser = argparse.ArgumentParser() 

    commands = parser.add_subparsers(dest="command")
    commands.required = True

    init_parser = commands.add_parser("init")
    init_parser.set_defaults(func=init) # Eğer kullanıcı init komutunu kullanırsa, çalıştırılacak fonksiyon olarak init fonksiyonu atanır.

    #ugit.py hash-object <dosya> şeklinde yeni bir komut tanımlar## Yukaridaki init gibi
    hash_object_parser = commands.add_parser("hash-object")
    hash_object_parser.set_defaults(func=hash_object)# tanimli olan hash_object fonksiyonunu calistirir
    hash_object_parser.add_argument("file")# Burada farkli olan komutun bir tane zorunlu arguman alacagini belirtmesi:file

    #ugit.py cat-file <object> şeklindeki komutları tanır 
    #This command is the "opposite" of hash-object:it can print an object bu its OID.
    cat_file_parser = commands.add_parser("cat-file")
    cat_file_parser.set_defaults(func=cat_file)
    cat_file_parser.add_argument("object")

    write_tree_parser = commands.add_parser("write-tree")
    write_tree_parser.set_defaults(func=write_tree)

    read_tree_parser = commands.add_parser("read-tree")
    read_tree_parser.set_defaults(func=read_tree)
    read_tree_parser.add_argument("tree")

    commit_parser = commands.add_parser("commit")
    commit_parser.set_defaults(func =commit)
    commit_parser.add_argument("-m", "--message", required=True)

    log_parser = commands.add_parser("log")
    log_parser.set_defaults(func=log)
    
    checkout_parser = commands.add_parser("checkout")
    checkout_parser.set_defaults(func=checkout)
    checkout_parser.add_argument("oid")

    return parser.parse_args()
 

def init(args):
    data.init()
    print(f'Initialized empty ugit repository in {os.getcwd()}/{data.GIT_DIR}')


def hash_object(args):
    with open(args.file, "rb") as f:
        print(data.hash_object(f.read()))


def cat_file (args):
    sys.stdout.flush ()
    sys.stdout.buffer.write (data.get_object (args.object, expected = None))


def write_tree(args):
    print(base.write_tree())


def read_tree(args):
    base.read_tree(args.tree)

def commit(args):
    print(base.commit(args.message))


def log(args):
    oid = args.oid or data.get_HEAD()
    while oid:
        commit = base.get_commit(oid)

        print(f'commit {oid}\n')
        print (textwrap.indent (commit.message, '    '))
        print("")

        oid = commit.parent


def checkout(args):
    base.checkout(args.oid)



