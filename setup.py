from setuptools import setup, find_packages

setup(
    name='gamarts',
    author="Tanguy Dugas du Villard",
    author_mail="tanguy.dugas01@gmail.com",
    version='1.1.0',
    description="Gamarts is a python library providing a unique way to represent static and animated surfaces in pygame, alongside with a clever loading and unloading behavior.",
    packages=find_packages(),
    install_requires=[
        'pygame',
        'pygame-cv',
        'ZOCallable',
        'pillow'
    ],
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Tanguy-ddv/gamarts",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Games/Entertainment",
        "Topic :: Software Development :: Libraries :: pygame"
    ],
    python_requires='>=3.6'
)