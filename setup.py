from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in aec/__init__.py
from aec import __version__ as version

setup(
	name="aec",
	version=version,
	description="ds",
	author="ds",
	author_email="ds",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
