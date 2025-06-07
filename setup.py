# setup.py - Professional package setup

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="fraud-detection-pipeline",
    version="1.0.0",
    author="Tylor Tian",
    author_email="tylortian0@gmail.com",
    description="High-performance fraud detection system with ML-powered anomaly detection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tylortian/fraud-detection-pipeline",
    packages=find_packages(exclude=["tests", "tests.*", "docs", "scripts"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "pytest-asyncio>=0.18",
            "black>=22.0",
            "isort>=5.0",
            "flake8>=4.0",
            "mypy>=0.910",
            "pre-commit>=2.0",
        ],
        "streaming": [
            "kafka-python>=2.0",
            "confluent-kafka>=1.7",
        ],
    },
    entry_points={
        "console_scripts": [
            "fraud-detector=fraud_detection.cli:main",
        ],
    },
)
