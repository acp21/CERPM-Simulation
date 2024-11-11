from setuptools import find_packages
from setuptools import setup

setup(
    name='turtlesim_msgs',
    version='1.9.2',
    packages=find_packages(
        include=('turtlesim_msgs', 'turtlesim_msgs.*')),
)
