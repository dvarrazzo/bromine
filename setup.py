import setuptools

with open("README.md") as f:
    long_description = f.read()

setuptools.setup(
    name="gambit-bromine",
    version="0.3.1",
    author="Daniele Varrazzo",
    author_email="piro@gambitresearch.com",
    description="Pythonic web testing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GambitResearch/bromine",
    packages=setuptools.find_packages(),
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, <4",
    classifiers="""
        Development Status :: 4 - Beta
        Framework :: Pytest
        Intended Audience :: Developers
        License :: OSI Approved :: MIT License
        Operating System :: OS Independent
        Programming Language :: Python :: 2.7
        Programming Language :: Python :: 3
        Topic :: Internet :: WWW/HTTP :: Browsers
        Topic :: Software Development :: Testing
        """.strip().splitlines(),
    install_requires=["six", "selenium>=3.141,<3.142"],
)
