# rosinenpicker

![Python Packaging](https://github.com/joheli/rosinenpicker/workflows/Packaging/badge.svg) ![PyPI](https://img.shields.io/pypi/v/rosinenpicker?label=PyPI) ![PyPI - Downloads](https://img.shields.io/pypi/dm/rosinenpicker)

'Rosinenpicker' is German for 'cherry picker' (never mind that 'Rosine' actually means *raisin*). Be it as it may - cherry picking is what `rosinenpicker` has been designed to do. It goes through a list of documents to extract *just those juicy bits* **you** are interested in. It uses regular expressions to accomplish this. But please do read on to learn how to use the program. 

# Installation

Please fire up your console and type:

```
pip install rosinenpicker
```

This should add the executable `rosinenpicker` to `PATH`, making it accessible from the console.

# Usage

Please type

```
rosinenpicker -c config_file -d database_file
```

where `config_file` (default: `config.yml`) and `database_file` (default: `matches.db`) represent a yml-formatted configuration file (please see sample [config.yml](configs/config.yml), which is more or less self-explanatory) and a sqlite database file (automatically created if not present), respectively.

For help type

```
rosinenpicker -h
```
