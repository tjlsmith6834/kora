from setuptools import setup, find_packages

setup(
    name="storage_retrieval_services",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "boto3",
        "botocore",
        "sqlalchemy",
    ],
    description="Storage functions for [Your Project]",
    author="Your Name",
    author_email="you@example.com",
)