from setuptools import setup, find_packages

package_name = "weblinx"
version = {}
with open(f"{package_name}/version.py") as fp:
    exec(fp.read(), version)

with open("README.md") as fp:
    long_description = fp.read()

extras_require = {
    "dev": ["black", "wheel"],
    "video": ["opencv-python-headless", "numpy", "Pillow"],
    "processing": ["lxml"],
    "eval": ["sacrebleu", "numpy", "pandas", "tqdm"],
}
# Dynamically create the 'all' extra by combining all other extras
extras_require["all"] = sum(extras_require.values(), [])

setup(
    name=package_name,
    version=version["__version__"],
    author="McGill NLP",
    author_email=f"{package_name}@googlegroups.com",
    url=f"https://github.com/McGill-NLP/{package_name}",
    description=f"The official {package_name} library",
    long_description=long_description,
    packages=find_packages(include=[f"{package_name}*"]),
    package_data={package_name: ["_data/*.json"]},
    install_requires=[
        "tqdm",
    ],
    extras_require=extras_require,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    # Cast long description to markdown
    long_description_content_type="text/markdown",
)
