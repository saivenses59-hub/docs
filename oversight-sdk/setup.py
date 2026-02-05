from setuptools import setup, find_packages

setup(
    name="oversight-sdk",
    version="1.0.2", # CHANGE THIS TO 1.0.2
    description="The Institutional Banking & Compliance Protocol for AI Agents.",
    long_description="OVERSIGHT PROTOCOL: The first financial safety layer for AI Agents. Prevents runaway spending and automates tax compliance.",
    long_description_content_type="text/plain", # Simplified to plain text to ensure it shows up
    author="Oversight Protocol",
    url="https://oversight-protocol.vercel.app",
    packages=find_packages(),
    install_requires=["requests", "pydantic"],
)