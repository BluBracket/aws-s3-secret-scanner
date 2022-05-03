# cli-recipes
BluBracket CLI Recipes. This repo contains sample code snippets demonstrate how to use BLuBracket CLI tool 
to scan for secrets and other risks programmatically.

# How to Install the BluBracket CLI

## Install with standalone executables

Use these direct links to download the executables:

- macOS: https://static.blubracket.io/cli/latest/blubracket-macos
- Linux: https://static.blubracket.io/cli/latest/blubracket-linux
- Windows: https://static.blubracket.io/cli/latest/blubracket-win.exe

# Recipes

## AWS S3

`recipes/aws_s3.py` demonstrates how to scan a S3 bucket.

Sample invocation: `pipenv run python -u recipes/aws_s3.py my-bucket`

To see more options `pipenv run python -u recipes/aws_s3.py --help`
