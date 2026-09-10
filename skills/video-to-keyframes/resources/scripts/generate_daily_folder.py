import argparse
from datetime import datetime
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("base_dir", nargs="?", default=".")
    parser.add_argument("--format", default="%Y-%m-%d")
    args = parser.parse_args()

    base_dir = Path(args.base_dir).expanduser().resolve()
    folder_name = datetime.now().strftime(args.format)
    target_dir = base_dir / folder_name
    target_dir.mkdir(parents=True, exist_ok=True)
    print(str(target_dir))


if __name__ == "__main__":
    main()
