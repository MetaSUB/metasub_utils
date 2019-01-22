"""This script is meant to do a health check for all of the
MetaSUB data files on Athena.

It should do the following
- verify each file is properly gzipped
- verify each file has a number of lines divisible by 4
- verify each file with a mate has the same number of lines as its mate
- output a table of number of lines and md5 checksums for all files
"""

from subprocess import run, PIPE, CalledProcessError
from os.path import abspath
import click


def run_cmd(cmd):
    process = run(cmd, shell=True, stdout=PIPE, check=True)
    return process.stdout.decode('utf-8')


def md5_sum(filename):
    cmd = f'openssl md5 -binary {filename} | base64'
    checksum = run_cmd(cmd).strip()
    return checksum


def process_one_file(filename, logger):
    """Return the number of lines in the file."""
    try:
        line_count = run_cmd(f'set -o pipefail && gunzip -c {filename}| wc -l')
    except CalledProcessError:
        logger(f'[ERROR] gzip_issue {filename}')
        return 0, None

    line_count = int(line_count)
    if line_count % 4 != 0:
        logger(f'[ERROR] bad_line_count {line_count} {filename}')
        return 0, None

    return line_count, md5_sum(filename)


def process_one_filepair(f1_name, f2_name, logger):
    """Check that both files are well formed and match."""
    l1, md51 = process_one_file(f1_name, logger)
    l2, md52 = process_one_file(f2_name, logger)
    if l1 != l2:
        logger(f'[ERROR] mismatched_line_count {l1} {l2} {f1_name} {f2_name}')
        return 0, None, None
    return l1, md51, md52


@click.command()
@click.option('-p/-s', '--paired/--single', default=True)
@click.argument('log_filename')
@click.argument('err_filename', type=click.File('a'))
@click.argument('filenames', nargs=-1)
def main(paired, log_filename, err_filename, filenames):
    """Run a health check for data on Athena."""
    filenames = [abspath(filename) for filename in filenames]
    log_tbl = {}
    with open(log_filename) as log_file:
        for line in log_file:
            filename, md5sum, line_count = line.split('\t')
            log_tbl[filename] = (md5sum, line_count)

    filenames = sorted([filename for filename in filenames if filename not in log_tbl])
    logger = lambda val: err_filename.write(val + '\n')
    with open(log_filename, 'a') as log_file:
        if paired:
            paired_files = [(filenames[i], filenames[i + 1]) for i in range(0, len(filenames) - 1, 2)]
            for f1_name, f2_name in paired_files:
                click.echo(f'{f1_name} {f2_name}', err=True)
                lines, md51, md52 = process_one_filepair(f1_name, f2_name, logger)
                if not lines:
                    continue
                log_file.write(f'{f1_name}\t{md51}\t{lines}\n')
                log_file.write(f'{f2_name}\t{md52}\t{lines}\n')
        else:
            for filename in filenames:
                click.echo(f'{filename}', err=True)
                lines, md5 = process_one_file(filename, logger)
                if not lines:
                    continue
                log_file.write(f'{filename}\t{md5}\t{lines}\n')


if __name__ == '__main__':
    main()
