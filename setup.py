from setuptools import find_packages, setup

setup(
    name="abstractions",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic",
        "asyncio",
        "libcst",
        "pydantic",
        "setuptools",
        # Add other dependencies here
    ],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            # Define any command-line scripts here
        ],
    },
)
