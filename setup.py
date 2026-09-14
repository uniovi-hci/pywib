from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]


setup(
    name='pywib',
    packages=find_packages(),
    version='1.1.2',
    description='HCI Web Interaction Analyzer - A library for analyzing web user interactions',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HumanCommunicationInteraction/pywib",
    packages=find_packages(),
    author='Guillermo Dylan Carvajal Aza & Alejandro Varela Álvarez',
    author_email='carvajalguillermo@uniovi.es',
    keywords=['HCI', 'Web Interaction', 'Analyzer'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)