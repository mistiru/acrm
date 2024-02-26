import shlex
import subprocess

from acrm.commands._base import BaseCommand


class LsCommand(BaseCommand):
    name = 'ls'
    description = "List packages contained on a remote repository"

    def handle(self):
        self.fetch_repository()

        command = f'tar tf "{self.config.db_file}"'
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
        table.set_header_title(self.config.repo_name)
        table.set_headers(['Package name', 'version'])
        for package in packages:
            name, *rest = package.rsplit('-', maxsplit=2)
            table.add_row([name, '-'.join(rest)])
        self.line('')
        table.render()
