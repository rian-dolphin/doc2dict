from setuptools import setup, find_packages

setup(
    name="doc2dict",
    version="0.2.4",
    packages=find_packages(),
    install_requires=['selectolax','xmltodict'
    ],
    python_requires=">=3.8"
)