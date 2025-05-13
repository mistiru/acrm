from cleo.application import Application
from cleo.helpers import option

from acrm.__version__ import __version__
from acrm.commands.add import AddCommand
from acrm.commands.dl import DlCommand
from acrm.commands.ls import LsCommand
from acrm.commands.rm import RmCommand


def main():
    application = Application(name='acrm', version=__version__)
    application.definition.add_options([
        option(
            long_name='user',
            short_name='u',
            description="The remote user that owns the repository",
            flag=False,
        ),
        option(
            long_name='host',
            short_name='H',
            description="The host that hosts the repository",
            flag=False,
        ),
        option(
            long_name='remote_root',
            short_name='r',
            description="The remote path to the repository root",
            flag=False,
        ),
        option(
            long_name='repository',
            short_name='d',
            description="The name of the repository (defaults to directory name)",
            flag=False,
        ),
    ])
    application.add(AddCommand())
    application.add(DlCommand())
    application.add(LsCommand())
    application.add(RmCommand())
    application.run()


if __name__ == '__main__':
    main()
