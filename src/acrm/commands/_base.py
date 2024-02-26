import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from cleo.commands.command import Command

TMP_ROOT = Path.home() / '.cache' / 'acrm' / 'repositories'


@dataclass
class RepoConfig:
    user: str | None
    host: str
    remote_root: Path
    repo_name: str
    arch: str

    @property
    def full_host(self) -> str:
        if self.user is None:
            return self.host
        else:
            return f'{self.user}@{self.host}'

    @property
    def local_path(self) -> Path:
        local_path = TMP_ROOT / self.repo_name / self.arch
        local_path.mkdir(mode=0o700, parents=True, exist_ok=True)
        return local_path

    @property
    def db_file(self) -> Path:
        db_file = self.local_path / f'{self.repo_name}.db'
        return db_file.resolve()


class BaseCommand(Command):

    def __init__(self) -> None:
        self._config: RepoConfig | None = None
        super().__init__()

    @property
    def config(self) -> RepoConfig:
        if self._config is None:
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

            self._config = RepoConfig(
                user=user,
                host=host,
                remote_root=remote_root,
                repo_name=repo,
                arch=arch,
            )

        return self._config

    def fetch_repository(self) -> None:
        self.line('Fetching repository...', style='info')

        command = (f'rsync -rtlvH --delete --safe-links'
                   f' "{self.config.full_host}:{self.config.remote_root}/"'
                   f' "{self.config.local_path}"')
        if subprocess.run(
            shlex.split(command),
            stdout=subprocess.DEVNULL if not self.io.is_verbose() else None,
        ).returncode:
            sys.exit(1)
