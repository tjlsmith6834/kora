from setuptools import setup, find_packages

setup(
    name="utils",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "PyPDF2",
    ],
    description="Utils for jobs-service",
    author="Tyler Smith",
    author_email="you@example.com",
)