# cli-recipes
BluBracket CLI Recipes. This repo contains sample code snippets demonstrate how to use BLuBracket CLI tool 
to scan for secrets and other risks programmatically.

# How to Install the BluBracket CLI

## Install with standalone executables

For example, to download and run the latest BluBracket CLI on macOS, you could run:

```
curl https://static.blubracket.com/cli/latest/macos/blubracket -o blubracket
chmod +x ./blubracket
mv ./blubracket /usr/local/bin/
```

Use these direct links to download the executables:

- macOS: https://static.blubracket.com/cli/latest/macos/blubracket
- Linux: https://static.blubracket.com/cli/latest/linux/blubracket
- Windows: https://static.blubracket.com/cli/latest/win/blubracket.exe

## Install with NPM

TODO


# Recipes

See `recipes` folder for all the available recipes

## AWS S3

`recipes/aws_s3.py` demonstrates how to scan a S3 bucket.

Sample invocation: `pipenv run python recipes/aws_s3.py my-bucket`

To see more options `pipenv run python recipes/aws_s3.py --help`
