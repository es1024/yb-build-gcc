import subprocess
import shlex
import os
import sys

from typing import List

from build_gcc.helpers import run_cmd, ChangeDir, BUILD_GCC_SCRIPTS_ROOT_PATH


def build_remotely(
        remote_server: str,
        remote_build_scripts_path: str,
        remote_mkdir: bool) -> None:
    assert remote_server is not None
    assert remote_build_scripts_path is not None
    assert remote_build_scripts_path.startswith('/')

    def run_ssh_cmd(ssh_args: List[str]) -> None:
        run_cmd(['ssh', remote_server] + ssh_args)

    quoted_remote_path = shlex.quote(remote_build_scripts_path)

    if remote_mkdir:
        run_ssh_cmd(['mkdir -p %s' % quoted_remote_path])

    with ChangeDir(BUILD_GCC_SCRIPTS_ROOT_PATH):
        excluded_files_str = subprocess.check_output(
            ['git', '-C', '.', 'ls-files', '--exclude-standard', '-oi', '--directory'])
        assert os.path.isdir('.git')
        excluded_files_path = os.path.join(os.getcwd(), '.git', 'ignores.tmp')
        with open(excluded_files_path, 'wb') as excluded_files_file:
            excluded_files_file.write(excluded_files_str)

        run_cmd([
            'rsync',
            '-avh',
            '--delete',
            '--exclude', '.git',
            '--exclude-from=%s' % excluded_files_path,
            '.',
            '%s:%s' % (remote_server, remote_build_scripts_path)])

        remote_bash_script = 'cd %s && bin/build_gcc.sh %s' % (
            quoted_remote_path,
            ' '.join(shlex.quote(arg) for arg in sys.argv[1:])
        )
        # TODO: why exactly do we need shlex.quote here?
        run_ssh_cmd(['bash', '-c', shlex.quote(remote_bash_script.strip())])
