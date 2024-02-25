# Arch Linux Custom Repository Manager

[![PyPI - Version](https://img.shields.io/pypi/v/acrm)](https://pypi.org/project/acrm/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/acrm)](https://pypi.org/project/acrm/)
[![PyPI - License](https://img.shields.io/pypi/l/acrm)](https://pypi.org/project/acrm/)

This program is intended to manage an Arch Linux custom repository hosted on a server accessible through `rsync`
(for example, on a VPS or a NAS with a `/path/to/www` folder served over the web by a web server).

It works by synchronizing the remote repository on the local machine using `rsync`, and then mainly uses `repo-add` to
manage this repository to finally synchronizing back to the remote server.

It requires to run on an Arch Linux distribution, and simply behaves as a wrapper around some common programs:

|                         Program                         |    From package    | Used for                                        |
|:-------------------------------------------------------:|:------------------:|:------------------------------------------------|
|    [uname](https://man.archlinux.org/man/uname.1.fr)    | core/**coreutils** | Detecting the architecture of the local machine |
|     [rsync](https://wiki.archlinux.org/title/rsync)     |  extra/**rsync**   | Synchronizing the repository                    |
|       [tar](https://man.archlinux.org/man/tar.1)        |    core/**tar**    | Reading inside the repository database          |
|     [GnuPG](https://wiki.archlinux.org/title/GnuPG)     |   core/**gnupg**   | Signing the packages and the repository         |
| [repo-add](https://man.archlinux.org/man/repo-add.8.en) |  core/**pacman**   | Managing the packages in the repository         |

> [!NOTE]
> The CLI of this program is made with [cleo](https://github.com/python-poetry/cleo),
> used by [poetry](https://python-poetry.org/).

## Global options

| Option        | Short | Required | Description                                                                    |
|:--------------|:------|:--------:|:-------------------------------------------------------------------------------|
| `host`        | `H`   |   yes    | Specify the host on which the repository is hosted                             |
| `remote_root` | `r`   |   yes    | The path to the repository, on the remote host                                 |
| `user`        | `u`   |    no    | The remote user who owns the repository<br/>Defaults to the current local user |
| `repository`  | `d`   |    no    | The name of the repository<br/>Defaults to the name of the directory           |

> [!IMPORTANT]
> Currently, some options are required by the CLI as it is the only way to pass information to the ACRM.

## Commands

### ls

List all the packages with their version in the repository.

```bash
acrm -H my_vps_or_nas -r /home/vps_user/path/to/my/repository ls
```

```
+------ repository ------+
| Package name | version |
+--------------+---------+
| acrm         | 0.1.0-1 |
+--------------+---------+
```
