from setuptools import setup

import python_flights

setup(
    name='python_flights',
    version=python_flights.__version__,
    packages=['python_flights'],
    url='https://github.com/sylvaus/python_flights',
    license='MIT',
    author='sylvaus',
    description='Wrapper for RapidAPI interface to SkyScanner API',
    requires=["requests"]
)
