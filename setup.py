from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

with open("freshbooks/VERSION") as f:
    version = f.readlines()[0].strip()

setup(
    name="freshbooks-sdk",
    version=version,
    author="Andrew McIntosh",
    author_email="andrew@amcintosh.net",
    description="API client for FreshBooks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/freshbooks/freshbooks-python-sdk",
    download_url="https://github.com/freshbooks/freshbooks-python-sdk/archive/release/{}.tar.gz".format(version),
    keywords=["FreshBooks"],
    license="MIT",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    install_requires=open("requirements.txt").readlines(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ]
)
