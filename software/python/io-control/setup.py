#!/usr/bin/env python3
from setuptools import setup, find_packages
from glob import glob

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()
name = 'io-control'
setup(name=name
    version='0.0.1',
    description='High level functionality of device',
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author='Simon Hobbs',
    author_email='simon.hobbs@electrooptical.net',
    license='MIT',
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Linux",
    ],
    python_requires='>=3.6',
    install_requires=[
        'click',
        'numpy',
        'timeout_decorator',
        'scipy',
    ],
    test_suite='nose.collector',
    tests_require=['nose'],
    scripts=list(glob("bin/*.py")),
    entry_points={
            'console_scripts': [
                f'{name}={name}:main',
            ]
    },
    include_package_data=True,
    zip_safe=True)
