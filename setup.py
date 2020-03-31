import setuptools
import re

with open("canoser/version.py", "r") as fp:
    try:
        version = re.findall(
            r"^version = \"([0-9\.]+)\"", fp.read(), re.M
        )[0]
    except IndexError:
        raise RuntimeError("Unable to determine version.")



with open("README.md", "r") as fh:
    content = fh.read()
    arr = content.split("\n")
    long_description = "\n".join(arr[4:])


tests_require = [
    'pytest',
    'hypothesis',
]


install_requires = [
]


setuptools.setup(
    name="canoser",
    version=version,
    author="yuan xinyu",
    author_email="yuan_xin_yu@hotmail.com",
    description="A python implementation of the LCS(Libra Canonical Serialization) for the Libra network.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yuan-xy/canoser-python.git",
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    tests_require=tests_require,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
