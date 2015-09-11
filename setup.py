#!/usr/bin/env python

from setuptools import setup
import os

stdlib = map(lambda x: "pylisp/stdlib/" + x, os.listdir("pylisp/stdlib"))
tests = map(lambda x: "pylisp/test/" + x, os.listdir("pylisp/test"))
data_files = [
        ("pylisp/stdlib", stdlib),
        ("pylisp/test", tests)]

setup(
        name = "Pylisp",
        version = "0.1",
        author = "pavpanchekha",
        author_email = "pavpanchekha@gmail.com",
        packages = ["pylisp"],
        scripts = ["pylisp/pylisp"],
        url = "http://pypi.python.org/pypi/pylisp/",
        license = "LICENSE.txt",
        description = "A lisp for pythonistas",
        long_description = open("README.rst").read(),
        data_files = data_files,
    )
