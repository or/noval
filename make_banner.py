#!/usr/bin/env python
import argparse
from PIL import Image

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--top-border", type=int, default=20,
        help="how much image data from the top to use for the filling")
    parser.add_argument(
        "--bottom-border", type=int, default=20,
        help="how much image data from the bottom to use for the filling")
    parser.add_argument(
        "--factor", type=float, default=1.5,
        help="height * factor will be the new height")
    parser.add_argument(
        "--offset", type=float, default=0.3,
        help="the vertical position of the old image, 0 means at the top, 1 at the bottom")
    parser.add_argument("input")
    parser.add_argument("output")

    args = parser.parse_args()

    img = Image.open(args.input)

    (width, height) = img.size
    new_height = round(height * args.factor)
    new_img = Image.new("RGB", (width, new_height))
    y_offset = round((new_height - height) * args.offset)
    new_img.paste(img, (0, y_offset))

    top_border = img.crop((0, 0, width, args.top_border))
    y = y_offset
    while y >= 0:
        top_border = top_border.transpose(Image.FLIP_TOP_BOTTOM)
        y -= top_border.size[1] - 1
        new_img.paste(top_border, (0, y))

    bottom_border = img.crop((0, height - args.bottom_border, width, height))
    y = y_offset + height
    while y < new_height:
        bottom_border = bottom_border.transpose(Image.FLIP_TOP_BOTTOM)
        new_img.paste(bottom_border, (0, y))
        y += bottom_border.size[1] - 1

    new_img.save(args.output)
