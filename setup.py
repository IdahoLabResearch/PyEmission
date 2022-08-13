import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

NAME = "PyEmission"
VERSION = "0.3.7"
DESCRIPTION = "PyEmission is a Python library for the estimation of gasoline vehicular emissions and fuel consumption"
URL = "https://github.com/IdahoLabResearch/PyEmission"
AUTHORS = "Md Mamunur Rahman; Ruby Nguyen"
EMAIL = "mdmamunur.rahman@inl.gov"
LICENSE = "Apache-2.0"
REQUIRED = ["numpy", 
            "pandas", 
            "matplotlib"]

PACKAGES = find_packages()


setup(
    name = NAME,
    version = VERSION,
    description = DESCRIPTION,
    long_description=README,
    long_description_content_type="text/markdown",
    url = URL,
    author = AUTHORS,
    author_email = EMAIL,
    license = LICENSE,
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7'
        ],
    install_requires = REQUIRED,
    packages = PACKAGES,
    include_package_data=True,
    package_data={'': ['*.pkl', '*xlsx']},

)

