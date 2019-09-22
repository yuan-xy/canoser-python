import setuptools
from canoser.version import version

with open("README.md", "r") as fh:
    content = fh.read()
    arr = content.split("\n")
    long_description = "\n".join(arr[4:])

setuptools.setup(
    name="canoser",
    version=version,
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
