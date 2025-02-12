import sys
from pypdf import PdfWriter
from os.path import getsize


def main(
    file_path: str,
    min_size: str = None,
    max_size: str = None,
) -> None:
    min_size = int(min_size) if min_size else 20
    max_size = int(max_size) if max_size else 1024
    file_size = getsize(file_path) // 1024
    quality = 80
    delta = 10

    while not (min_size <= file_size <= max_size):
        writer = PdfWriter(clone_from=file_path)
        for page in writer.pages:
            for img in page.images:
                img.replace(img.image, quality=quality)

        with open("out.pdf", "wb") as f:
            writer.write(f)

        file_size = getsize("out.pdf") // 1024

        if file_size > max_size:
            quality -= delta
        elif file_size < min_size:
            delta //= 2
            quality = quality + delta

    print(f"Succesfully compressed {file_path} to {file_size} KB @ quality {quality}%!")


if __name__ == '__main__':
    main(*sys.argv[1:])