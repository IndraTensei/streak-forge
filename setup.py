from setuptools import setup, find_packages

setup(
    name="streak-forge",
    version="1.0.0",
    description="Build unbreakable habits with beautiful terminal streak tracking",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="IndraTensei",
    url="https://github.com/IndraTensei/streak-forge",
    py_modules=["streak_forge"],
    python_requires=">=3.8",
    install_requires=[
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "streak-forge=streak_forge:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Utilities",
    ],
)
