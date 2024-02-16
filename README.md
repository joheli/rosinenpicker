# rosinenpicker

![Python Packaging](https://github.com/joheli/rosinenpicker/workflows/Packaging/badge.svg) ![PyPI](https://img.shields.io/pypi/v/rosinenpicker?label=PyPI) ![PyPI - Downloads](https://img.shields.io/pypi/dm/rosinenpicker)

[Deutsch](README_DE.md)

# Manual

Welcome to `rosinenpicker`! This tool is like a magical sieve that helps you find golden nuggets (or "Rosinen") of information within a mountain of documents. It's designed for anyone who needs to extract specific pieces of information without diving deep into the technicalities.

## Understanding Key Terms

- **Command Line**: A text-based interface to operate your computer. Imagine telling your computer exactly what to do by typing in commands.
- **YAML**: A simple configuration file format used by `rosinenpicker` to understand your instructions. It's easy to read and write.
- **Arguments**: Special instructions you provide to `rosinenpicker` when you start it, telling it where to find its instructions (YAML file) and where to store its findings.

## Getting Started

0. **Python 3.11 is a prerequisite**: Make sure you have Python 3.11 or above installed. There are various ways to install Python, but I recommend [Miniconda](https://docs.anaconda.com/free/miniconda/index.html).

1. **Installation**: First, let's bring `rosinenpicker` to your computer. Open your command line and type:

   ```
   pip install rosinenpicker
   ```

2. **Running the Program**: To launch `rosinenpicker`, enter the following:

   ```
   rosinenpicker -c path/to/your_config.yml -d path/to/your_database.db
   ```

   Replace `path/to/your_config.yml` with the actual path to your configuration file, and `path/to/your_database.db` with where you'd like to save the findings. (If not specified, the configuration and database files are assumed to be `config.yml` and `matches.db` in your current directory; also, the database is automatically created if it is not present on your system.)

## Creating Your YAML Configuration

Here's a sample configuration to guide `rosinenpicker`:

```yaml
title: 'My Document Search'
strategies:
  strategy1:
    processed_directory: '/path/to/documents'
    file_name_pattern: '.*\.pdf'
    file_format: 'pdf'
    terms:
      term1: 'apple pie'
    export_format: 'csv'
    export_path: '/path/to/export.csv'
```

This tells `rosinenpicker` to look in `/path/to/documents` for PDF files containing "apple pie" and save results in a CSV file at `/path/to/export.csv`. Fur further information, check out the [sample configuration file](configs/config.yml) in this repository - the file contains additional comments you may find useful.

### Going deeper

Now of course it is not very useful to just extract the term "apple pie" out of documents. But you can do much more. Instead of "apple pie" you can enter a regular expression, e.g. "\d{8}" to extract numbers consisting of exactly eight digits. But there's more: if you enter an expression along with "@@@" (which stands for "variable string"), only a match to "@@@" is returned. E.g. "Name: @@@" will return whatever follows "Name:"! 

## Using `rosinenpicker`

With your `config.yml` ready, go back to the command line and run `rosinenpicker` with the `-c` and `-d` arguments as shown above.

## Help and Options

For a list of commands and options, type:

```
rosinenpicker -h
```

This command displays all you need to know to navigate `rosinenpicker`.

## Conclusion

You're all set to explore and extract valuable information with `rosinenpicker`. Happy information hunting!
