import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="canoser",
    version="0.1.3",
    author="yuan xinyu",
    author_email="yuanxinyu.hangzhou@gmail.com",
    description="A python implementation of the LCS(Libra Canonical Serialization) for the Libra network.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yuan-xy/canoser-python.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)