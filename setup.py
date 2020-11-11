from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

with open("freshbooks/VERSION") as f:
    version = f.readlines()[0].strip()

setup(
    name="freshbooks-python-sdk",
    version=version,
    author="Andrew McIntosh",
    author_email="andrew@amcintosh.net",
    description="API client for FreshBooks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/amcintosh/freshbooks-python-sdk",
    download_url="https://github.com/amcintosh/freshbooks-python-sdk/archive/{}.tar.gz".format(version),
    keywords=["FreshBooks"],
    license="MIT",
    packages=find_packages(exclude=["*.test", "*.test.*"]),
    include_package_data=True,
    install_requires=open("requirements.txt").readlines(),
)
