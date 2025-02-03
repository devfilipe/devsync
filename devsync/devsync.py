#!/usr/bin/env python3
import argparse
import sys
import os
import json
import subprocess

from devsync.lsyncd_conf_handler import load_config, save_config


def parse_args():
    parser = argparse.ArgumentParser(description="devsync: Seamlessly manage and synchronize your lsyncd configuration files with ease.")
    parser.add_argument("--conf", "-c", required=False, help="Lua configuration file (.conf.lua)")
    parser.add_argument("--source", "-s", help="Absolute path or '.' for the source directory")
    parser.add_argument("--target", "-t", help="Target directory path")
    # parser.add_argument("--include", "-i", help="Comma-separated list of files to include")
    # parser.add_argument("--exclude", "-e", help="Comma-separated list of files to exclude")
    # parser.add_argument("--on-event", help='JSON with events, e.g.: \'[{"file": "a.txt", "cmd": "echo a.txt > events.txt"}]\'')
    parser.add_argument("--port", "-p", type=int, help="SSH port")
    parser.add_argument(
        "--binary",
        "-b",
        default="~/devsync/scripts/binary.sh",
        help="Path to binary handler. If not provided, the binary option is not added.",
    )
    parser.add_argument("--handler", help="Handler name")
    parser.add_argument("--alias", "-a", help="Sync identifier label")
    parser.add_argument("--list", "-l", action="store_true", help="List configured syncs")
    parser.add_argument(
        "--delete",
        "-d",
        action="store_true",
        help="Remove sync entries matching source and target (and optionally alias)",
    )

    parser.add_argument(
        "--lsyncd-restart",
        nargs="?",
        const="",
        help="Restart lsyncd process; optionally specify config file path for matching",
    )
    parser.add_argument(
        "--lsyncd-stop",
        nargs="?",
        const="",
        help="Stop lsyncd process; optionally specify config file path for matching",
    )
    parser.add_argument("--lsyncd-list", action="store_true", help="List lsyncd processes")

    return parser.parse_args()


def list_syncs(syncs):
    if not syncs:
        print("No sync entries found.")
        return
    for sync in syncs:
        alias = sync.get("alias", "(no alias)")
        source = sync.get("source", "N/A")
        target = sync.get("target", "N/A")
        print(f"Alias: {alias} | Source: {source} | Target: {target}")


def add_sync_entry(syncs, args):
    if not args.source or not args.target:
        print("Error: To add a sync you must specify --source and --target.")
        sys.exit(1)
    if args.binary:
        binary = f"{args.binary}"
    entry = {
        "alias": args.alias,
        "source": os.path.abspath(args.source) if args.source != "." else os.getcwd(),
        "target": args.target,
        # "include": args.include.split(",") if args.include else [],
        # "exclude": args.exclude.split(",") if args.exclude else [],
        # "on_event": json.loads(args.on_event) if args.on_event else [],
        "port": args.port if args.port else 22,
        "binary": binary,
    }
    syncs.append(entry)
    print("Sync added successfully!")
    return syncs


def delete_sync_entry(syncs, args):
    # If alias is provided, remove based solely on alias.
    if args.alias:
        new_syncs = [sync for sync in syncs if sync.get("alias", "") != args.alias]
        removed = len(syncs) - len(new_syncs)
        if removed:
            print(f"{removed} entry(ies) removed based on alias '{args.alias}'.")
        else:
            print("No matching entry found to remove by alias.")
        return new_syncs
    else:
        # Otherwise, require source and target to remove the sync entry.
        if not args.source or not args.target:
            print("Error: To remove a sync by source and target, you must specify --source and --target.")
            sys.exit(1)
        source = os.path.abspath(args.source) if args.source != "." else os.getcwd()
        target = args.target
        new_syncs = []
        for sync in syncs:
            # Remove if both source and target match.
            if sync.get("source") == source and sync.get("target") == target:
                continue
            else:
                new_syncs.append(sync)
        removed = len(syncs) - len(new_syncs)
        if removed:
            print(f"{removed} entry(ies) removed.")
        else:
            print("No matching entry found to remove by source and target.")
        return new_syncs


def main():
    args = parse_args()

    config_file = args.conf
    syncs = load_config(config_file)

    if args.list:
        list_syncs(syncs)
        sys.exit(0)

    if args.lsyncd_list:
            result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
            for line in result.stdout.splitlines():
                if "lsyncd" in line and "--lsyncd-list" not in line:
                    print(line)
            sys.exit(0)

    if args.lsyncd_stop is not None:
        config_filter = args.lsyncd_stop.strip() if args.lsyncd_stop != "" else None
        result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
        pids = []
        for line in result.stdout.splitlines():
            if "lsyncd" in line:
                if config_filter and config_filter not in line:
                    continue
                parts = line.split()
                pids.append(parts[1])
        for pid in pids:
            subprocess.run(["kill", pid])
        print(f"Stopped {len(pids)} lsyncd process(es)")
        sys.exit(0)

    if args.lsyncd_restart is not None:
        config_filter = args.lsyncd_restart.strip() if args.lsyncd_restart != "" else None
        # Stop lsyncd processes
        result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
        pids = []
        for line in result.stdout.splitlines():
            if "lsyncd" in line and "--lsyncd-restart" not in line:
                if config_filter and config_filter not in line:
                    continue
                parts = line.split()
                pids.append(parts[1])
        for pid in pids:
            subprocess.run(["kill", pid])
        # Start lsyncd
        if config_filter:
            subprocess.Popen(["lsyncd", config_filter])
            print("lsyncd restarted with config:", config_filter)
        else:
            subprocess.Popen(["lsyncd"])
            print("lsyncd restarted (all)")
        sys.exit(0)

    if args.handler:
        handler_dir = os.path.expanduser(f"~/devsync/scripts/{args.handler}_handler")
        os.makedirs(handler_dir, exist_ok=True)
        with open(os.path.join(handler_dir, "handler.sh"), "w") as f:
            f.write('/usr/bin/rsync "$@"\n')
            f.write('result=$?\n')
            f.write('(\n')
            f.write('  if [ $result -eq 0 ]; then\n')
            f.write(f'     source ~/devsync/scripts/{args.handler}_handler/{args.handler}.sh\n')
            f.write('  fi\n')
            f.write(') >/dev/null 2>/dev/null </dev/null\n')
            f.write('exit $result\n')
        with open(os.path.join(handler_dir, f"{args.handler}.sh"), "w") as f:
            f.write('#!/bin/bash\n')
            f.write(f'# echo "OK" > /tmp/devsync-{args.handler}-handler.txt\n')
            f.write(f"# /usr/bin/sshpass -p '<SECRET>' ssh <USER>@<ADDRESS> 'echo OK > /tmp/devsync-{args.handler}-handler.txt'\n")
        sys.exit(0)

    # Delete sync entry
    if args.delete:
        syncs = delete_sync_entry(syncs, args)
        save_config(config_file, syncs)
        sys.exit(0)

    # Add new sync entry
    syncs = add_sync_entry(syncs, args)
    save_config(config_file, syncs)


if __name__ == "__main__":
    main()
