# devsync

```bash
devsync --help
```

```bash
usage: devsync [-h] [--conf CONF] [--source SOURCE] [--target TARGET] [--port PORT] [--binary BINARY] [--handler HANDLER] [--alias ALIAS] [--list]
               [--delete] [--lsyncd-restart [LSYNCD_RESTART]] [--lsyncd-stop [LSYNCD_STOP]] [--lsyncd-list]

devsync: Seamlessly manage and synchronize your lsyncd configuration files with ease.

options:
  -h, --help            show this help message and exit
  --conf CONF, -c CONF  Lua configuration file (.conf.lua)
  --source SOURCE, -s SOURCE
                        Absolute path or '.' for the source directory
  --target TARGET, -t TARGET
                        Target directory path
  --port PORT, -p PORT  SSH port
  --binary BINARY, -b BINARY
                        Path to binary handler. If not provided, the binary option is not added.
  --handler HANDLER     Handler name
  --alias ALIAS, -a ALIAS
                        Sync identifier label
  --list, -l            List configured syncs
  --delete, -d          Remove sync entries matching source and target (and optionally alias)
  --lsyncd-restart [LSYNCD_RESTART]
                        Restart lsyncd process; optionally specify config file path for matching
  --lsyncd-stop [LSYNCD_STOP]
                        Stop lsyncd process; optionally specify config file path for matching
  --lsyncd-list         List lsyncd processes
```

## Getting Started

```bash
git clone https://github.com/devfilipe/devsync.git
cd devsync
poetry install

poetry run devsync --help
```

## Install Initial Conf and Scripts (Optional)

Currently, the scripts are not installed by default. You can install them by running the following command:

```bash
devsync-dist

#rsync -av --ignore-existing "$(poetry run python -c 'import pathlib; print((pathlib.Path(__file__).parent / "scripts").resolve())')" ~/devsync/scripts/
```

```bash
/home/${USER}/devsync
├── conf
│   └── lsyncd.conf.lua
└── scripts
    └── test_handler
        ├── handler.sh
        └── test.sh
```

## Usage

```bash
# a) sync to remote
devsync -c ~/devsync/conf/lsyncd.conf.lua -s /tmp/local/server -t user@address:/tmp/remote/server -p 22  -a server

# b) delete
devsync -c ~/devsync/conf/lsyncd.conf.lua -a server -d

# c) generate post-transfer handler scripts (to be used with --binary)
devsync --handler restart
# edit ~/devsync/scripts/restart_handler/restart.sh
# update scripts permissions

# d) sync to remote with binary
devsync -c ~/devsync/conf/lsyncd.conf.lua -s /tmp/local/server -t user@address:/tmp/remote/server -p 22  -a server --binary ~/devsync/scripts/restart_handler/handler.sh # handler.sh executes restart.sh on remote server

# e) lsyncd commands
devsync --lsyncd-restart
devsync --lsyncd-stop
devsync --lsyncd-list

# f) list lsyncd sync entries
devsync -c ~/devsync/conf/lsyncd.conf.lua --list
Alias: server | Source: /tmp/local/server | Target: user@address:/tmp/remote/server
```

## Development

```bash
git clone https://github.com/devfilipe/devsync.git
cd devsync
poetry install
poetry shell
devsync --help
```

## lsyncd

Steps to install lsyncd on Manjaro

```bash
# Install the required packages:
sudo pacman -S install git base-devel
sudo pacman -S asciidoc cmake lua53-posix

# Clone the git repository:
git clone https://aur.archlinux.org/lsyncd.git

# Enter the git repository and build the package:
cd lsyncd && makepkg

# Find the package in the current working directory
# Install the package:
sudo pacman -U lsyncd-VERSION-PACKAGE-NAME.pkg.tar.zst
```
