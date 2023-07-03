#!/usr/bin/env python3

from distutils.core import setup

setup(
    name="vstpreset",
    version="0.1.0",
    description="simple module for reading and writing VST3 presets ",
    author="Jan Minor",
    author_email='39484083+janminor@users.noreply.github.com',
    url="https://github.com/janminor/python-vstpreset",
    packages=["vstpreset"],
    classifiers=[  
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
    ],
    python_requires=">=3.7, <4",
)
