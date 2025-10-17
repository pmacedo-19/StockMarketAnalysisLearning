from setuptools import setup, find_packages

setup(
    name="stock-market-analysis",
    packages=find_packages(),
    install_requires=[
        "Flask",
        "Flask-SQLAlchemy",
        "python-dotenv",
        "requests",
        "pytest",
    ],
)