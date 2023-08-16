from setuptools import setup, find_packages


# Read dependencies from 'requirements.txt'
f = open("requirements.txt", "r")
lines = f.readlines()
lines = [line.strip() for line in lines]


setup(
    name="RiskconcileData",
    author="Ruben Kerkhofs",
    version="3.4.0",
    packages=find_packages(),
)
