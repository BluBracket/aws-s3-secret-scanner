# AWS S3 Risk Scanner

Demonstrates how to scan a AWS S3 bucket for various risks

## How to Install the BluBracket CLI

To run the scanner, BluBracket CLI must be installed first.

### Install with standalone executables

For example, to download and run the latest BluBracket CLI on macOS, you could run:

```
curl https://static.blubracket.com/cli/latest/blubracket-macos -o blubracket
chmod +x ./blubracket
mv ./blubracket /usr/local/bin/
```

Use these direct links to download the executables:

- macOS: https://static.blubracket.com/cli/latest/blubracket-macos
- Linux: https://static.blubracket.com/cli/latest/blubracket-linux
- Windows: https://static.blubracket.com/cli/latest/blubracket-win.exe

### Install with NPM

TODO


## Usage

```
pipenv sync 
pipenv run python aws_s3_risk_scanner.py my-bucket
```

To see more options `pipenv run python aws_s3_risk_scanner.py --help`

