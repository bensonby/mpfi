import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mpfi",
    version="0.0.17",
    author="Benson Yeung",
    author_email="bensonby@gmail.com",
    description="FIS Prophet Model Point File Inspector and Processor",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bensonby/mpfi",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "pandas",
    ],
    python_requires='>=3.6',
)
