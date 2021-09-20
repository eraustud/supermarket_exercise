import setuptools

with open("README.md", 'r', encoding='utf-8') as rm:
    full_description = rm.read()

setuptools.setup(
    name="supermarket",
    version="0.1",
    author="eraustud",
    author_email="notpublic@example.com",
    long_description=full_description,
    url="https://github.com/eraustud/supermarket_exercise",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.7"
)