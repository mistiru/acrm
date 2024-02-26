from acrm.commands._base import BaseCommand


class LsCommand(BaseCommand):
    name = 'ls'
    description = "List packages contained on a remote repository"

    def handle(self):
        table = self.table()
        table.set_header_title(self.repo_config.repo_name)
        table.set_headers(['Package name', 'version'])
        for package in self.packages.values():
            table.add_row([package.name, package.version])
        self.line('')
        table.render()
