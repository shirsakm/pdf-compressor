import sys
from pypdf import PdfWriter
from os.path import getsize, exists
import logging


def main(
    file_path: str,
    min_size: str = None,
    max_size: str = None,
) -> None:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    if not exists(file_path):
        logging.error(f"File not found: {file_path}")
        return

    try:
        min_size = int(min_size) if min_size else 20
        max_size = int(max_size) if max_size else 1024
    except ValueError as e:
        logging.error(f"Invalid min_size or max_size: {e}")
        return

    if min_size >= max_size:
        logging.error("min_size must be less than max_size")
        return

    file_size = getsize(file_path) // 1024
    quality = 80
    delta = 10

    try:
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
                delta = max(1, delta // 2)
                quality = min(100, quality + delta)
            
            logging.info(f"Current file size: {file_size} KB, quality: {quality}%")

            if quality <= 0:
                logging.warning("Quality reached 0, compression may not be effective.")
                break

    except Exception as e:
        logging.error(f"An error occurred during compression: {e}")
        return

    print(f"\nSuccesfully compressed {file_path} to {file_size} KB @ {quality}% quality!")


if __name__ == '__main__':
    main(*sys.argv[1:])