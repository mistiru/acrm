from cleo.helpers import argument, option

from acrm.commands._base import BaseCommand


class RmCommand(BaseCommand):
    name = 'rm'
    description = "Remove a package from a remote repository"
    arguments = [
        argument(
            'package_name',
            description="The package to upload",
        ),
    ]
    options = [
        option(
            'key',
            'k',
            description="The GPG key to use to sign the repo",
            flag=False,
        ),
    ]

    def handle(self):
        package_name = self.argument('package_name')
        key = self.option('key')

        self.remove_package(package_name=package_name, key=key)

        self.update_repository()
