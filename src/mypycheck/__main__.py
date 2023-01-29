import argparse

from . import clean, check

parser = argparse.ArgumentParser()
parser.add_argument('target', nargs='?')
parser.add_argument('--clean', action='store_true')
args = parser.parse_args()

if args.clean:
    clean()

if args.target:
    check(args.target)
