from setuptools import setup, find_packages

setup(
    name="doc2dict",
    version="0.01",
    packages=find_packages(),
    install_requires=['selectolax'
    ],
    python_requires=">=3.8"
)