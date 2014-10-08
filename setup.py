#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name='ppp_core',
    version='0.1',
    description='Core/router of the PPP framework',
    url='https://github.com/ProjetPP/PPP-Core',
    author='Valentin Lorentz',
    author_email='valentin.lorentz+ppp@ens-lyon.org',
    license='MIT',
    classifiers=[
        'Environment :: No Input/Output (Daemon)',
        'Development Status :: 1 - Planning',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
    packages=[
        'ppp_core',
    ],
)


