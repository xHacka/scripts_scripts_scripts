#!/usr/bin/python3
# Source: https://gist.github.com/xHacka/10c22906e0819a8ba3f6e44d7bab2f71

import os
import click
import tempfile
from pathlib import Path
from subprocess import check_output, run

GHIDRA_PATH = os.environ.get('GHIDRA_PATH', '/opt/ghidra/')
ANALYZER = f"{GHIDRA_PATH}support/analyzeHeadless"
GHIDRA_RUN = f"{GHIDRA_PATH}ghidraRun"
GHIDRA_EXTENSION = '.gpr'


def analyze(project, project_name, filename, verbose):
    command = f"{ANALYZER} '{project}' '{project_name}' -import '{filename}'"
    if not verbose:
        command += " >/dev/null"
    run(command, shell=True)


def start(project):
    command = f"{GHIDRA_RUN} '{project}'"
    run(command, shell=True)


def file(filename):  # Run `file` Command
    return '\t' + ''.join(
        check_output(["file", filename.absolute()])
        .decode()
        .split(': ', maxsplit=1)[1]
        .replace(', ', '\n\t')
    ).strip()


def pwn_checksec(filename):
    try:  # Run pwntools `checksec`
        click.secho(f"[+] Pwntools Checksec:\n", fg='green')
        command = f'pwn checksec --file {filename}'
        check_output(command.split())
    except:
        click.secho(f"[-] Checksec Failed...", fg='red')
    finally:
        return


@click.command()
@click.argument('filename', type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option('-t', '--temp', 'temp', is_flag=True, help="Make project temporary")
@click.option('-v', '--verbose', 'verbose', is_flag=True, default=False, help="Add verbositiy to analyzer")
@click.option('-c', '--checksec', 'checksec', is_flag=True, default=False, help="Use pwntools checksec to check securities of binary")
def main(filename, temp, verbose, checksec):
    filename = Path(filename.replace(' ', '_'))

    project = f'{Path.cwd()}' if not temp else tempfile.mkdtemp()
    project = project.replace(' ', '_')
    project_name = f'{project}/{filename.stem}{GHIDRA_EXTENSION}'

    if filename.suffix == GHIDRA_EXTENSION:
        click.secho("[+] Project Exists... Opening...", fg="yellow")
        start(project_name)
        return

    click.secho(f"[*] File Ouput:\n{file(filename)}", fg='green')

    if checksec:
        pwn_checksec(filename)

    click.secho(f"[*] Running Analysis...", fg='green')
    analyze(project, filename.stem, filename, verbose)

    click.secho(f"[+] Analysis Complete\n[*] Opening Ghidra...", fg='green')
    start(project_name)

    click.secho(f"[*] Project Directory: {project}", fg='green')
    click.secho(f"[*] Project File: {project_name}", fg='green')


if __name__ == '__main__':
    '''
    Automatically open and analyze the given binary
    or open already created project
    '''
    main()