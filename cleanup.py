import argparse
import logging
import sys
import time
from pathlib import Path

PROTECTED = {
    Path("/"), Path("/bin"), Path("/boot"), Path("/etc"), Path("/home"),
    Path("/lib"), Path("/lib64"), Path("/opt"), Path("/root"),
    Path("/sbin"), Path("/usr"), Path("/var"),
}
DEFAULT_PATTERNS = ["*.log", "*.log.*", "*.tmp", "*.tar.gz", "*.zip", "*.jar"]

logger = logging.getLogger("cleanup")


def parse_args():
    parser = argparse.ArgumentParser(description="Delete old logs and artifacts.")
    parser.add_argument("directory", type=Path, help="Directory to clean")
    parser.add_argument("--days", type=int, default=14, help="Age threshold in days")
    parser.add_argument("--pattern", nargs="+", default=DEFAULT_PATTERNS,
                        help="Filename patterns to match")
    parser.add_argument("--dry-run", action="store_true", help="Show only, don't delete")
    parser.add_argument("--log-file", type=Path, default=None,
                        help="Also write log to this file")
    return parser.parse_args()


def setup_logging(log_file):
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=handlers,
    )


def validate(directory, days):
    """Return an error message if the input is unsafe, else None."""
    if not directory.is_dir():
        return f"Not a directory: {directory}"
    if directory.resolve() in PROTECTED:
        return f"Refusing to clean protected path: {directory.resolve()}"
    if days < 1:
        return "--days must be at least 1"
    return None


def find_old_files(directory, patterns, days):
    """Yield regular files matching a pattern and older than `days`."""
    cutoff = time.time() - days * 86400
    seen = set()
    for pattern in patterns:
        for p in directory.rglob(pattern):
            if p in seen:
                continue
            seen.add(p)
            if p.is_symlink() or not p.is_file():
                continue
            if p.stat().st_mtime < cutoff:
                yield p


def cleanup(directory, patterns, days, dry_run):
    """Delete (or report) old files. Return (processed, errors)."""
    processed = errors = 0
    for p in find_old_files(directory, patterns, days):
        if dry_run:
            logger.info("[DRY-RUN] Would delete %s", p)
            processed += 1
            continue
        try:
            p.unlink()
            logger.info("Deleted %s", p)
            processed += 1
        except PermissionError:
            logger.error("Permission denied: %s", p)
            errors += 1
        except OSError as exc:
            logger.error("Failed to delete %s: %s", p, exc)
            errors += 1
    return processed, errors


def main():
    args = parse_args()
    setup_logging(args.log_file)

    problem = validate(args.directory, args.days)
    if problem:
        logger.error(problem)
        return 2

    logger.info("Starting cleanup of %s (older than %d days)", args.directory, args.days)
    processed, errors = cleanup(args.directory, args.pattern, args.days, args.dry_run)
    logger.info("Done. Files processed: %d, errors: %d", processed, errors)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
