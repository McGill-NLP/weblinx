"""
Given a path to a directory, convert all images in the directory to webp format.
"""
import  argparse
from pathlib import Path

from PIL import Image

def convert_to_webp(directory: str, height: int = None, quality: int = 80):
    directory = Path(directory)
    exts = ['*.jpg', '*.jpeg', '*.png']
    for ext in exts:
        for im_path in directory.glob(ext):
            im = Image.open(im_path)
            # if height is provided, resize the image
            if height:
                im = im.resize((int(im.width * height / im.height), height))
            
            im.save(im_path.with_suffix('.webp'), 'webp', quality=quality)

def main():
    parser = argparse.ArgumentParser(description='Convert all images in a directory to webp format.')
    parser.add_argument('-d', '--directory', type=str, help='Path to the directory containing images.')
    parser.add_argument('--height', type=int, help='New height of the output image. If this is provided, we will resize the image to this height.')
    parser.add_argument('--quality', type=int, help='Quality of the output image.', default=80)
    args = parser.parse_args()
    # convert to dict
    convert_to_webp(**vars(args))
    
if __name__ == '__main__':
    main()