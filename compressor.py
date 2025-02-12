import sys
from pypdf import PdfWriter
from os.path import getsize


def main(file_path: str) -> None:
    writer = PdfWriter(clone_from=file_path)
    print(f"in Kb: {getsize(file_path) // 1024}")


if __name__ == '__main__':
    main(file_path=sys.argv[1])