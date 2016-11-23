#!/usr/bin/env python

from argparse import ArgumentParser
from difflib import SequenceMatcher
import os
import pickle

class Diff(object):

    def __init__(self, name):
        self._name = name
        self._left = None
        self._right = None

    @property
    def name(self):
        return self._name

    @property
    def left(self):
        return self._left

    @property
    def right(self):
        return self._right

    @left.setter
    def left(self, value):
        self._left = value

    @right.setter
    def right(self, value):
        self._right = value

    def is_added(self):
        return self._left is None and self._right is not None

    def is_removed(self):
        return self._left is not None and self._right is None

    def is_modified(self):
        return self._left is not null and self._right is not None

    def __str__(self):
        diff_str = self.name + '\n'
        if self.left:
            diff_str += " <- '{0}'\n".format(self.left)
        if self.right:
            diff_str += " -> '{0}'\n".format(self.right)
        return diff_str


IGNORE_LIST = ['_', 'WINDOWID', 'OLDPWD', 'DISPLAY', 'SSH_CLIENT',
               'SSH_CONNECTION', 'SSH_TTY', 'XDG_SESSION_ID']


def compute_diff(env1, env2, include_all=False):
    diffs = {}
    for name, value in env1.iteritems():
        if name not in env2:
            diff = Diff(name)
            diff.left = value
            diffs[name] = diff
        elif value != env2[name]:
            diff = Diff(name)
            diff.left = value
            diff.right = env2[name]
            diffs[name] = diff
    for name, value in env2.iteritems():
        if name not in env1:
            diff = Diff(name)
            diff.right = value
            diffs[name] = diff
    if not include_all:
        for name in IGNORE_LIST:
            if name in diffs:
                del diffs[name]
    return diffs


def show_opcodes(str1, str2, junk=':'):
    junk_func = lambda x: x == junk
    seq_matcher = SequenceMatcher(junk_func, str1, str2)
    for opcode in seq_matcher.get_opcodes():
        op = opcode[0]
        left = str1[opcode[1]:opcode[2]].strip(junk)
        right = str2[opcode[3]:opcode[4]].strip(junk)
        if op == 'insert' and opcode[1] == 0:
            print("prepend '{0}'".format(right))
        elif op == 'insert' and opcode[2] == len(str1):
            print("append '{0}'".format(right))
        elif op != 'equal':
            print("{op} '{left}' -> '{right}'".format(op=op,
                                                      left=left,
                                                      right=right))
    

def read_ignore(file_name):
    ignore = []
    with open(file_name, 'r') as ignore_file:
        for line in ignore_file:
            line = line.strip()
            if line and not line.startswith('#'):
                ignore.extend(line.strip().split(';'))
    return ignore

if __name__ == '__main__':
    arg_parser = ArgumentParser(description='read environment from '
                                            'file, and compare to '
                                            'current environment')
    arg_parser.add_argument('file',
                            help='file to read environment frmo')
    arg_parser.add_argument('--all', action='store_true',
                            help='show all variables')
    arg_parser.add_argument('--var', help='variable to detail')
    arg_parser.add_argument('--ignore',
                            help='file containing environment '
                                             'variables to ignore')
    arg_parser.add_argument('--sep', default=':',
                            help='character separating values')
    options = arg_parser.parse_args()
    if options.ignore:
        IGNORE_LIST = read_ignore(options.ignore)
    with open(options.file, 'rb') as env_file:
        prev_env = pickle.load(env_file)
    curr_env = os.environ
    diffs = compute_diff(prev_env, curr_env, options.all)
    if options.var:
        name = options.var
        show_opcodes(diffs[name].left, diffs[name].right,
                     options.sep)
    else:
        for name in sorted(diffs.iterkeys()):
            print(diffs[name])
