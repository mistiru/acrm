from cleo.helpers import argument, option

from acrm.commands._base import BaseCommand


class AddCommand(BaseCommand):
    name = 'add'
    description = "Add a package to a remote repository"
    arguments = [
        argument(
            'package_file',
            description="The package to add",
        ),
    ]
    options = [
        option(
            'key',
            'k',
            description="The GPG key to use to sign the package and repo",
            flag=False,
        ),
    ]

    def handle(self):
        package_file_name = self.argument('package_file')
        key = self.option('key')

        self.add_package(package_file_name=package_file_name, key=key)

        self.update_repository()
