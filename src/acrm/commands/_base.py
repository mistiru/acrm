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


@dataclass
class Package:
    name: str
    version: str
    file: Path | None
    sig_file: Path | None


class BaseCommand(Command):

    def __init__(self) -> None:
        super().__init__()
        self._repo_config: RepoConfig | None = None
        self._packages: dict[str, Package] | None = None

    @property
    def repo_config(self) -> RepoConfig:
        if self._repo_config is None:
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

            self._repo_config = RepoConfig(
                user=user,
                host=host,
                remote_root=remote_root,
                repo_name=repo,
                arch=arch,
            )

        return self._repo_config

    def _fetch_repository(self) -> None:
        self.line('Fetching repository...', style='info')

        command = (f'rsync -rtlvH --delete --safe-links'
                   f' "{self.repo_config.full_host}:{self.repo_config.remote_root}/"'
                   f' "{self.repo_config.local_path}"')
        if subprocess.run(
            shlex.split(command),
            stdout=subprocess.DEVNULL,
        ).returncode:
            self.line_error("An error occurred while fetching repository", style='error')
            sys.exit(1)

    @property
    def packages(self) -> dict[str, Package]:
        if self._packages is None:
            self._fetch_repository()

            command = f'tar tf "{self.repo_config.db_file}"'
            raw_list: str = subprocess.run(
                shlex.split(command),
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
            ).stdout.decode().strip()
            raw_packages: list[str] = [
                line.rstrip('/')
                for line in raw_list.split('\n')
                if not line.endswith('desc')
            ]

            self._packages: dict[str, Package] = {}
            for raw_package in raw_packages:
                name, *rest = raw_package.rsplit('-', maxsplit=2)
                version = '-'.join(rest)
                file = next((
                    file
                    for file in self.repo_config.local_path.glob(f'{raw_package}-*.pkg.tar.*')
                    if not file.name.endswith('.sig')
                ), None)
                sig_file = next((
                    file
                    for file in self.repo_config.local_path.glob(f'{raw_package}-*.pkg.tar.*.sig')
                ), None)
                self._packages[name] = Package(
                    name=name,
                    version=version,
                    file=file,
                    sig_file=sig_file,
                )

        return self._packages

    def remove_package(self, package_name: str, key: str | None) -> None:
        if package_name not in self.packages:
            self.line_error(f"Package \"{package_name}\" not found in repository", style='error')
            sys.exit(1)

        key_option = f'-k {key}' if key else ''
        command = (f'repo-remove -v -s {key_option}'
                   f' "{self.repo_config.db_file}"'
                   f' "{package_name}"')
        if subprocess.run(
            shlex.split(command),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode:
            self.line_error("An error occurred while removing the package", style='error')
            sys.exit(1)
        if (file := self.packages[package_name].file) is not None:
            file.unlink()
        if (sig_file := self.packages[package_name].sig_file) is not None:
            sig_file.unlink()

    def update_repository(self) -> None:
        self.line('Updating repository...', style='info')

        command = (f'rsync -rtlvH --delete --safe-links'
                   f' "{self.repo_config.local_path}/"'
                   f' "{self.repo_config.full_host}:{self.repo_config.remote_root}"')
        if subprocess.run(
            shlex.split(command),
            stdout=subprocess.DEVNULL,
        ).returncode:
            self.line_error("An error occurred while updating repository", style='error')
            sys.exit(1)
