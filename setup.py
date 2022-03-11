from setuptools import setup
import os

VERSION = "0.1"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="image-diff",
    description="CLI tool for comparing images",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Simon Willison",
    url="https://github.com/simonw/image-diff",
    project_urls={
        "Issues": "https://github.com/simonw/image-diff/issues",
        "CI": "https://github.com/simonw/image-diff/actions",
        "Changelog": "https://github.com/simonw/image-diff/releases",
    },
    license="Apache License, Version 2.0",
    version=VERSION,
    packages=["image_diff"],
    entry_points="""
        [console_scripts]
        image-diff=image_diff.cli:cli
    """,
    install_requires=["click", "Pillow", "click-default-group"],
    extras_require={"test": ["pytest"]},
    python_requires=">=3.7",
)
