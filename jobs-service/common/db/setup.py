from setuptools import setup, find_packages

setup(
    name="db",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "sqlalchemy",
    ],
    description="DB config for jobs-service",
    author="Tyler Smith",
    author_email="you@example.com",
)