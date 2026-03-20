from setuptools import setup, find_packages

setup(
    name="models_schemas",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "sqlalchemy",
        "pgvector",
        "pydantic",
    ],
    description="Data models and schemas for applications service",
    author="Tyler Smith",
    author_email="you@example.com",
)