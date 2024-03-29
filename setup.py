import io
import os
import re

from setuptools import find_packages, setup


def read(filename):
    filename = os.path.join(os.path.dirname(__file__), filename)
    text_type = type(u'')
    with io.open(filename, mode = 'r', encoding = 'utf-8') as fd:
        return re.sub(text_type(r':[a-z]+:`~?(.*?)`'), text_type(r'``\1``'), fd.read())

def read_requirements():
    filename = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    with io.open(filename) as f:
        return [ine for line in f.read().splitlines() if (ine := str.lstrip(line)) if len(ine) > 0 if not ine.startswith('#')]


setup(
    name = 'Graph-State-Machine',
    version = '3.2', # Update in package __init__ too
    url = 'https://github.com/T-Flet/Graph-State-Machine',
    license = 'BSD 3-Clause',

    author = 'Thomas Fletcher',
    author_email = 'T-Fletcher@outlook.com',

    description = "A simple library to build easily interpretable computational constructs similar to a Turing machine over a graph, where states are combinations of a graph's (typed) nodes; an example use would be a transparent backend logic which navigates an ontology",
    long_description = read('README.rst'),

    packages = find_packages(exclude = ('tests',)),

    install_requires = read_requirements(),

    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12'
    ]
)
