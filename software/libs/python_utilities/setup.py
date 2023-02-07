#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(name='python_utilities',
      version='0.0.1',
      description='',
      long_description_content_type="text/markdown",
      url='https://github.com/snhobbs/python_utilities',
      author='Simon Hobbs',
      author_email='simon.hobbs@electrooptical.net',
      license='MIT',
      packages=find_packages(),
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
      python_requires='>=3.6',
      #install_requires=[],
      test_suite='nose.collector',
      tests_require=['nose'],
      scripts=[],
      include_package_data=True,
      zip_safe=True)
