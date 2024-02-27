import shutil
from pathlib import Path

from cleo.helpers import argument

from acrm.commands._base import BaseCommand


class DlCommand(BaseCommand):
    name = 'dl'
    description = "Download a copy of the selected package from a remote repository"
    arguments = [
        argument(
            'package_name',
            description="The package to upload",
        ),
    ]

    def handle(self):
        package_name = self.argument('package_name')

        package = self.get_package(package_name=package_name)

        shutil.copy(package.file, Path('.') / package.file.name)
        self.line(package.file.name)
