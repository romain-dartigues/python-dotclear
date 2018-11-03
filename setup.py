#!/usr/bin/env python
# vim:set fileencoding=utf8 ts=4 sw=4 et:

import io
import os
import re

_github_path = 'romain-dartigues/python-dotclear'
name = 'dotclear'

try:
    from setuptools import setup
except ImportError:
    import warnings
    from distutils.core import setup
    warnings.warn('unable to import setuptools, all options will not be available')

PWD = os.path.dirname(os.path.abspath(__file__))


with io.open(os.path.join(PWD, name, '__init__.py'), 'rt', encoding='utf8') as fobj:
    version = re.search(
        r'''^__version__\s*=\s*(?P<q>["'])(.*)(?P=q)''',
        fobj.read(),
        re.M,
    ).group(2)

with io.open('README.md', 'rt', encoding='utf8') as fobj:
    README = fobj.read()


setup(
    name=name,
    version=version,
    description='Dotclear wiki parser',
    long_description=README,
    author='Romain Dartigues',
    author_email='romain.dartigues@gmail.com',
    license='BSD 3-Clause License',
    keywords=[
        'dotclear',
        'wiki',
    ],
    url='https://github.com/{}'.format(_github_path),
    include_package_data=True,
    platforms='any',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Markup',
    ],
    packages=[name],
    extras_require={
        'dev': (
            'pytest>=3',
            'coverage',
        ),
    },
)
