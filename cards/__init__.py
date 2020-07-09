# Courtesy of Anurag Uniyal, via StackOverflow
from os.path import dirname, basename, isfile, join
from glob import glob
modules = glob(join(dirname(__file__), "*.py"))
__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]
