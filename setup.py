from setuptools import setup, find_packages
import os

# Single-source version information
__version__ = None
__license__ = None
__author__ = None
repo_root = os.path.join(os.path.dirname(__file__))
vers_file = os.path.join(repo_root, "nbtschematic", "version.py")
exec(open(vers_file).read())

with open('README.md') as readme:
    long_description = readme.read()


with open('requirements.txt') as requirements:
    dependencies = [line.strip() for line in requirements]


setup(
    name='nbtschematic',
    version=__version__,
    license=__license__,
    description='A simple schematic file reader for nbtlib',
    long_description=long_description,
    long_description_content_type='text/markdown',

    author=__author__,
    author_email='3526918+cbs228@users.noreply.github.com',
    url='https://github.com/cbs228/nbtschematic',

    platforms=['any'],
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='nbt schema minecraft mcschematic schematic package library',

    packages=find_packages(),

    install_requires=dependencies,
)
