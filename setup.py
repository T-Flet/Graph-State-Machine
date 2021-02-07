import io
import os
import re

from setuptools import find_packages
from setuptools import setup


def read(filename):
    filename = os.path.join(os.path.dirname(__file__), filename)
    text_type = type(u'')
    with io.open(filename, mode = 'r', encoding = 'utf-8') as fd:
        return re.sub(text_type(r':[a-z]+:`~?(.*?)`'), text_type(r'``\1``'), fd.read())


setup(
    name = 'Graph-State-Machine',
    version = '0.4.1', # Update in package __init__ too
    url = 'https://github.com/T-Flet/Graph-State-Machine',
    license = 'MIT',

    author = 'Thomas Fletcher',
    author_email = 'T-Fletcher@outlook.com',

    description = "A simple framework for building easily interpretable computational constructs between a graph automaton and a Turing machine where states are combinations of a graph's (typed) nodes; an example use would be as transparent backend logic by pathing through an ontology",
    long_description = read('README.rst'),

    packages = find_packages(exclude = ('tests',)),

    install_requires = [],

    classifiers = [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.8',
    ]
)
