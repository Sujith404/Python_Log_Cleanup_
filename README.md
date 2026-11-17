# Python_Log_Cleanup_
Cleaning up old logs and build artifacts on Linux servers using Python CLI


A small Python script that deletes old log files and build artifacts from a folder. I wrote it to practise Python scripting on Linux, based on a problem I see in real systems: logs and build output pile up until a disk fills.

You give it a folder and an age in days. It finds files that match (logs, temp files, zips, jars and so on) and haven't been modified in that long, then deletes them.

## Running it

Always do a dry run first. It shows what would be deleted and touches nothing:

    python3 cleanup.py /path/to/folder --days 14 --dry-run

If the list looks right, run it for real:

    python3 cleanup.py /path/to/folder --days 14

A few other options:

    python3 cleanup.py /path/to/folder --days 30 --log-file cleanup.log
    python3 cleanup.py /path/to/folder --pattern "*.jar" "*.zip"

By default it matches `*.log`, `*.log.*`, `*.tmp`, `*.tar.gz`, `*.zip` and `*.jar`. Anything else, like a `.txt` or `.pdf`, is left alone even if it's old.

## Why it's cautious

Deleting files can't be undone, so I tried to make it hard to do damage by accident:

- `--dry-run` previews the deletions.
- It refuses to run on system folders like `/`, `/etc`, `/usr` and `/var`.
- It skips symlinks, so it can't delete something outside the folder you pointed it at.
- If a file can't be deleted (usually permissions), it logs the error and moves on instead of crashing.

Every action is logged with a timestamp, to the screen and optionally to a file.

## Exit codes

- `0`: everything went fine
- `1`: ran, but some files couldn't be deleted
- `2`: bad input (folder doesn't exist, protected path, or invalid `--days`)

I added these so cron or Jenkins can tell whether a run worked.

## Scheduling it

I ran it from cron on an Amazon Linux EC2 instance. Cron has a minimal environment, so use full paths. This runs it every day at 2 AM:

    0 2 * * * /usr/bin/python3 /home/ec2-user/cleanup-lab/cleanup.py /path/to/folder --days 14 --log-file /home/ec2-user/cron-cleanup.log

## Trying it safely

`reset.sh` builds a small test folder with a few old files and a few new ones, so you can try the script without touching anything real. It expects to live in `~/cleanup-lab`.

## What it doesn't do (yet)

- It only goes by last-modified time, not file size.
- It doesn't remove empty folders afterwards.
- It has no automated tests. I tested it by hand.

If I keep working on it, tests with `pytest` would be next.

## Built with

Python 3 (argparse, pathlib, logging), Linux and cron.
