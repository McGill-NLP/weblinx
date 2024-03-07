"""
Given a path to a directory, convert all images in the directory to webp format.
"""
import  argparse
from pathlib import Path

from PIL import Image

def convert_to_webp(directory: str):
    directory = Path(directory)
    exts = ['*.jpg', '*.jpeg', '*.png']
    for ext in exts:
        for image in directory.glob(ext):
            img = Image.open(image)
            img.save(image.with_suffix('.webp'), 'webp')

def main():
    parser = argparse.ArgumentParser(description='Convert all images in a directory to webp format.')
    parser.add_argument('-d', '--directory', type=str, help='Path to the directory containing images.')
    args = parser.parse_args()
    convert_to_webp(args.directory)
    
if __name__ == '__main__':
    main()