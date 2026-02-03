# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="sls-memory",
    version="0.1.0",
    author="Zhengqianyi",
    description="A mem0-compatible memory SDK powered by Alibaba Cloud SLS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aliyun/aliyun-log-memory-sdk",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "alibabacloud-sls20201230>=3.0.0",
        "alibabacloud-tea-openapi>=0.3.0",
    ],
)
