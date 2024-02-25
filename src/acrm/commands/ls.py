import shlex
import subprocess
import sys
from pathlib import Path

from cleo.commands.command import Command

TMP_ROOT = Path.home() / '.cache' / 'acrm' / 'repositories'


class LsCommand(Command):
    name = 'ls'
    description = "List packages contained on a remote repository"

    def handle(self):
        user: str | None = self.option('user')
        host: str | None = self.option('host')
        if host is None:
            self.line_error("The \"--host\" option is required for now", style='error')
            sys.exit(1)
        remote_root: str | None = self.option('remote_root')
        if remote_root is None:
            self.line_error("The \"--remote_root\" option is required for now", style='error')
            sys.exit(1)
        remote_root: Path = Path(remote_root)
        repo: str | None = self.option('repository')
        if repo is None:
            repo = remote_root.name
        arch = subprocess.run(
            shlex.split('uname -m'),
            stdout=subprocess.PIPE,
        ).stdout.strip().decode()
        remote_root /= arch

        # Fetch the repo
        self.line('Fetching repository...', style='info')
        local_path = TMP_ROOT / repo / arch
        local_path.mkdir(mode=0o700, parents=True, exist_ok=True)
        command = (f'rsync -rtlvH --delete --safe-links'
                   f' "{f"{user}@" if user else ""}{host}:{remote_root}/"'
                   f' "{local_path}"')
        if subprocess.run(
            shlex.split(command),
            stdout=subprocess.DEVNULL if not self.io.is_verbose() else None,
        ).returncode:
            return

        # List packages
        db_file = local_path / f'{repo}.db'
        db_file = db_file.resolve()
        command = f'tar tf "{db_file}"'
        raw_list: str = subprocess.run(
            shlex.split(command),
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        ).stdout.decode().strip()
        packages: list[str] = [
            line.rstrip('/')
            for line in raw_list.split('\n')
            if not line.endswith('desc')
        ]
        table = self.table()
        table.set_header_title(repo)
        table.set_headers(['Package name', 'version'])
        for package in packages:
            name, *rest = package.rsplit('-', maxsplit=2)
            table.add_row([name, '-'.join(rest)])
        self.line('')
        table.render()
