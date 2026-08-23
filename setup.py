from setuptools import setup, find_packages

setup(
    name="prtiny",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "torch>=2.0.0",
        "torchvision>=0.15.0",
    ],
)
