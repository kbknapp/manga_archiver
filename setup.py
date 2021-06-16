import re
import codecs
import os
import setuptools

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with codecs.open(os.path.join(here, *parts), "r") as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ma",
    version=find_version("manga_archiver", "__init__.py"),
    author="Kevin K. <kbknapp@gmail.com>",
    description="A tool for archiving manga to CBR files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    scripts=["bin/ma"],
    packages=setuptools.find_packages(),
    test_requires=[
        "pytest"
    ],
    install_requires=[
        #"functools",
        "cssselect",
        "Pillow",
        "requests",
        "lxml",
        "cryptography",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
        "Topic :: System :: Installation/Setup",
    ],
    python_requires=">=3.7",
)
