from setuptools import setup, find_packages

setup(
    name="doc2dict",
    version="0.3.0",
    packages=find_packages(),
    install_requires=['selectolax','xmltodict','pypdfium2'
    ],
    python_requires=">=3.8"
)