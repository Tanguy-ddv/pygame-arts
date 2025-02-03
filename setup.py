from setuptools import setup, find_packages

setup(
    name='pygame-cv',
    author="Tanguy Dugas du Villard",
    author_mail="tanguy.dugas01@gmail.com",
    version='1.0.0',
    description="Pygame-arts is a python library providing a unique way to represent static and animated surfaces in pygame, alongside with a clever loading and unloading behavior.",
    packages=find_packages(),
    install_requires=[
        'pygame',
        'pygame-cv',
        'pillow',
        'ZOCallable'
    ],
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Tanguy-ddv/pygame-arts",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Games/Entertainment"
    ],
    python_requires='>=3.6'
)