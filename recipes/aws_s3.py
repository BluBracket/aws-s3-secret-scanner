import logging
import os
import subprocess
import sys
import tempfile

import boto3
import click
from dotenv import load_dotenv


@click.command()
@click.argument('bucket')
@click.option('--output', '-o', type=click.File("w"), help='Output file name to store found risks.')
def aws_s3(bucket, output):
    """Scans S3 bucket for risks using BluBracket CLI.
    BluBracket will skip over objects that are unscannable.
    """

    try:
        _aws_s3(bucket, output)
    except:
        logging.exception('')


def _aws_s3(bucket, output):
    load_dotenv()

    if not output:
        output = sys.stdout

    session = boto3.Session()
    s3 = session.resource('s3')
    bucket = s3.Bucket(bucket)

    for bucket_obj in bucket.objects.all():
        file_name = bucket_obj.key
        file_response = bucket_obj.get()
        scan_file(file_name, file_response, output)


def scan_file(file_name, file_response, output):
    """
    scan_file scans a single file
    :param file_name:
    :param file_response:
    :return:
    """
    try:
        _scan_file(file_name, file_response, output)
    except:
        logging.exception('')


def _scan_file(file_name, file_response, output):

    # directory or empty file
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
            # found risks will be stored in `cli_output_file_path`
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
                pass

            # note: CLI's scan-file command does not produce any output except on errors
            # so it is OK to stream the whole file (input body) first, without consuming the output,
            # and to collect any possible output only later.
            # so, it is OK to call `communicate` here.
            # In case there is a lot of output we would need to collect it asynchronously (in other thread),
            # to avoid a possible deadlock when both input and output pipes will be blocked.
            stdout, _ = cli_process.communicate()
            if stdout:
                raise Exception(stdout.decode('utf-8', 'replace'))

        # now have the file output, read it and send to stdout for now
        with open(cli_output_file_path, 'r') as cli_output_file:
            for line in cli_output_file.readlines():
                output.write(line)
                output.flush()

    finally:
        os.remove(cli_output_file_path)


if __name__ == '__main__':
    aws_s3()
