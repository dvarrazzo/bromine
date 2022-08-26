import setuptools

with open("README.md") as f:
    long_description = f.read()

setuptools.setup(
    name="gambit-bromine",
    version="0.4.1",
    author="Daniele Varrazzo",
    author_email="daniele.varrazzo@gmail.com",
    description="Pythonic web testing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dvarrazzo/bromine",
    packages=setuptools.find_packages(),
    python_requires=">=3.8",
    classifiers="""
        Development Status :: 4 - Beta
        Framework :: Pytest
        Intended Audience :: Developers
        License :: OSI Approved :: MIT License
        Operating System :: OS Independent
        Programming Language :: Python :: 3
        Topic :: Internet :: WWW/HTTP :: Browsers
        Topic :: Software Development :: Testing
        """.strip().splitlines(),
    install_requires=["selenium"],
    entry_points={"pytest11": ["bromine = bromine.pytest"]},
)
