# Casey H 2022
from setuptools import setup, find_packages

setup(
    name="bristol",
    install_requires=["sipyco"],
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "aqctl_bristol = bristol.aqctl_bristol:main",
        ],
    },
)
