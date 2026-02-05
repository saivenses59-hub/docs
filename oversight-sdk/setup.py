from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of your README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="oversight-sdk",
    version="1.0.1", # Increment the version!
    description="The Institutional Banking & Compliance Protocol for AI Agents.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Oversight Protocol",
    author_email="founder@oversight-protocol.ai",
    url="https://oversight-protocol.vercel.app",
    project_urls={
        "Documentation": "https://docs.oversight-protocol.ai",
        "Source": "https://github.com/your-username/oversight-protocol",
    },
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
        "pydantic>=2.0.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Office/Business :: Financial",
    ],
    python_requires=">=3.8",
)