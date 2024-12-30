from setuptools import setup, find_packages

__version__ = "0.1.2"

setup(
    name="burner",
    version=__version__,
    description="Subtitle generation with Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/rkulyassa/burner/",
    license="MIT",
    author="Ryan Kulyassa",
    author_email="rkulyassa@gmail.com",
    packages=find_packages(),
    install_requires=["numpy"],
)
