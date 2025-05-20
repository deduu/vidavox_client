from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# long_description read from your README.md
long_description = (here / "README.md").read_text(encoding="utf-16")

setup(
    name="vidavox-rag-client",              # ← your distribution name
    version="0.1.0",                         # ← your version
    author="Dedy Ariansyah",
    author_email="ariansyah@vidavox.ai",
    description="Client-side script to access the Vidavox RAG API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/deduu/vidavox_client.git",
    license="MIT",
    packages=find_packages(exclude=["tests", "examples"]),
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25",
        "pydantic>=1.8",

    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    entry_points={
        # if you have console_scripts, e.g.:
        # "console_scripts": ["rag-client=vidavox_rag_client.cli:main"]
    },
)
