import setuptools

with open("README.md") as f:
    long_description = f.read()

setuptools.setup(
    name="gambit-bromine",
    version="0.1",
    author="Daniele Varrazzo",
    author_email="piro@gambitresearch.com",
    description="Pythonic web testing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GambitResearch/bromine",
    packages=setuptools.find_packages(),
    classifiers="""
        Development Status :: 4 - Beta
        Programming Language :: Python :: 2
        Programming Language :: Python :: 3
        License :: OSI Approved :: MIT License
        Operating System :: OS Independent
        """.strip().splitlines(),
    # Note: selenium 3.14 is broken on https requests
    install_requires=["six", "selenium<3.14"],
)
