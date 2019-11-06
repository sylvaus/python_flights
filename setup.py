from setuptools import setup, find_packages

import python_flights

with open("readme.md", "r") as fh:
    long_description = fh.read()

setup(
    name='python_flights',
    version=python_flights.__version__,
    packages=find_packages(),
    url='https://github.com/sylvaus/python_flights',
    license='MIT',
    author='sylvaus',
    description='Wrapper for RapidAPI interface to SkyScanner API',
    long_description=long_description,
    long_description_content_type="text/markdown",
    requires=["requests"],
    python_requires='>3.7.0',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
