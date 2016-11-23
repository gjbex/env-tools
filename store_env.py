#!/usr/bin/env python

from argparse import ArgumentParser
import os
import pickle

if __name__ == '__main__':
    arg_parser = ArgumentParser(description='capture environment variables '
                                            'in a file for comparison')
    arg_parser.add_argument('file', help='file name to store environment')
    options = arg_parser.parse_args()
    with open(options.file, 'wb') as env_file:
        pickle.dump(os.environ, env_file)
