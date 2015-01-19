#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name='ppp_core',
    version='0.7.3',
    description='Core/router of the PPP framework.',
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
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
    install_requires=[
        'requests',
        'ppp_datamodel>=0.5.2,<0.7',
        'ppp_libmodule>=0.7,<0.8',
    ],
    packages=[
        'ppp_core',
    ],
)


