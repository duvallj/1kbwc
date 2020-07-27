# Courtesy of Anurag Uniyal, via StackOverflow
from glob import glob
from os.path import abspath, dirname, basename, isfile, join

modules = glob(join(dirname(abspath(__file__)), "*.py"))
__all__ = [basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]
