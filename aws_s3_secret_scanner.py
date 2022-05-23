import json
import logging
import os
import subprocess
import sys
import tempfile
import urllib.parse

import boto3
import click
import dotenv


@click.command()
@click.argument('bucket')
@click.option(
    '--output',
    '-o',
    type=click.File("w"),
    default=sys.stdout,
    help='Output file name to store found secrets. Defaults to stdout',
)
def scan_aws_s3_bucket(bucket, output):
    """
    Scans S3 bucket for secrets using BluBracket CLI.
    BluBracket will skip over objects that are unscannable.
    """

    _scan_aws_s3_bucket(bucket, output)


def _scan_aws_s3_bucket(bucket_name, out):
    dotenv.load_dotenv()

    session = boto3.Session()
    s3 = session.resource('s3')

    for bucket_obj in s3.Bucket(bucket_name).objects.all():
        file_name = bucket_obj.key
        file_response = bucket_obj.get()
        scan_file(bucket_name, file_name, file_response, out)


def scan_file(bucket_name, file_name, file_response, out):
    """
    Scans a single file
    Args:
        bucket_name:
        file_name:
        file_response:
        out:

    Returns:

    """

    try:
        _scan_file(bucket_name, file_name, file_response, out)
    except Exception:
        # for this recipe we just want to print the exception and continue scanning
        logging.exception(f'Error while scanning {file_name}')


def _scan_file(bucket_name, file_name, file_response, out):
    # skip a directory or an empty file
    if not file_response['ContentLength'] or 'application/x-directory' in file_response['ContentType']:
        click.echo(f'skipping {file_name}')
        return

    click.echo(f'scanning {file_name}')

    # we will output to a temp file
    fd, cli_output_file_path = tempfile.mkstemp()

    try:
        os.close(fd)  # only CLI will write to the file

        # run CLI as a subprocess to scan a single file
        # note: as there is no `--input` parameter, the input data will come from stdin
        cli_cmd = [
            "blubracket",
            # scan-file instructs CLI to scan a single file
            "scan-file",
            # specify the file name as there will be no file on local file system
            "--filename",
            file_name,
            # found secrets will be stored in `cli_output_file_path`
            "-o",
            cli_output_file_path,
        ]

        with subprocess.Popen(cli_cmd, stdin=subprocess.PIPE, stderr=subprocess.STDOUT) as cli_process:

            # stream the file through CLI
            # doing that allows us to avoid saving the whole file on local file system
            file_body = file_response['Body']
            try:
                for chunk in file_body.iter_chunks():
                    cli_process.stdin.write(chunk)
            except BrokenPipeError:
                # if CLI does no support handling of particular files, e.g. binary files
                # CLI will exit without reading the input data
                # this will lead to BrokenPipeError in stdin.write(chunk)
                # 'ignore' it as it is a real error
                click.echo(f'skipping {file_name}')

            # note: when `-o` option is specified, `scan-file` command does not produce any output except on errors
            # so it is OK to stream the whole file (input body) first, without consuming the output,
            # and to collect any possible output only later.
            # so, it is OK to call `communicate` here.
            # In case there is a lot of output we would need to collect it asynchronously (in other thread),
            # to avoid a possible deadlock when both input and output pipes will be blocked.
            stdout, _ = cli_process.communicate()
            if stdout:
                raise Exception(stdout.decode('utf-8', 'replace'))

        # before sending the found secrets to out, do some postprocessing
        # the secret result file is in json lines format, where each line represent the secret data
        with open(cli_output_file_path, 'r') as cli_output_file:
            for secret_line in cli_output_file.readlines():
                #  each line is a valid json object/dictionary
                secret = json.loads(secret_line)

                # remove some fields that not super useful
                if 'textual_context' in secret:
                    del secret['textual_context']
                if 'auto_dismiss' in secret:
                    del secret['auto_dismiss']

                # add some new fields

                # s3 uri
                secret['s3_uri'] = f's3://{bucket_name}/{file_name}'
                # url to access/download the file
                # Note to url to work file has to be publicly accessible
                secret['s3_object_url'] = f'https://{bucket_name}.s3.amazonaws.com/{urllib.parse.quote(file_name)}'
                # url to open file in AWS console
                secret[
                    's3_console_object_url'
                ] = f'https://s3.console.aws.amazon.com/s3/object/{bucket_name}?prefix={urllib.parse.quote(file_name)}'

                # now ready to store the secret in out
                secret_json = json.dumps(secret)
                out.write(secret_json)
                out.write('\n')
                out.flush()

    finally:
        os.remove(cli_output_file_path)


if __name__ == '__main__':
    scan_aws_s3_bucket()
