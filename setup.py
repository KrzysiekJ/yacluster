#!/usr/bin/env python

from setuptools import setup

VERSION = '1.0.0'


def read(file_name):
    with open(file_name, 'r') as f:
        return f.read()

setup(
    author='Krzysztof Jurewicz',
    author_email='krzysztof.jurewicz@gmail.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Scientific/Engineering :: GIS',
    ],
    description='''Distance-based clustering tool''',
    long_description=read('README.rst'),
    name='yacluster',
    py_modules=[
        'yacluster',
    ],
    url='http://github.com/KrzysiekJ/yacluster',
    version=VERSION,
)
