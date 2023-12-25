from setuptools import setup, find_packages

setup(
    name="abouter",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "tornado>=6.3",
        "pyyaml>=6.0",
        "motor>=3.1",
        "pydantic>=1.10,<2.0",
        "openai>=1.3.3",
        "tiktoken>=0.5.1"
    ],
)
