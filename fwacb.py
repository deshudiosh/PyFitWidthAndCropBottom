import sys
from pathlib import Path

import click
from PIL import Image, ImageOps

TARGET_WIDTH = 720
BOTTOM_MARGIN = 18

# def find_size_in_name(name: Path):
#     """" search for WWWxHHH in filename and return as tuple"""
#     try:
#         n = name.stem
#         extracted = [c if c in "1234567890x" else " " for c in n]
#         extracted = "".join(extracted).split()
#         extracted = [x for x in extracted if "x" in x]
#         extracted = extracted[0]
#
#         size = extracted.split("x")
#         size = tuple(map(int, size))
#         assert len(size) == 2
#     except:
#         size = None
#
#     return size
#
#
# def crop_if_needed(arg: Path):
#     """ Apply crop to image based on filename template: "filename_WWWxHHH.ext" """
#     expected_size = find_size_in_name(arg)
#     img = Image.open(arg) # type: Image.Image
#
#     # if image size doesn't match it's name
#     if expected_size != img.size and expected_size is not None:
#         img.crop((0, 0, *expected_size)).save(fp=arg, subsampling=0, quality=100)
#         click.echo(arg)
#         return img
#     else:
#         return None
#
#

def validate_image(arg) -> Path:
    """ Return if arg is existing file and is jpg or png"""
    p = Path(arg)
    return p if p.is_file() and p.suffix in ['.jpg', '.png'] else None


def img_fit(img: Image.Image) -> Image.Image:
    w, h = img.size

    if w > TARGET_WIDTH:
        new_height = round((720/w) * h)
        size = (TARGET_WIDTH, new_height)

        img = img.resize(size, Image.LANCZOS)

    return img


def is_line_white(img:Image.Image, width, line_num):
    is_white = True

    for x in range(width):
        color = img.getpixel((x, line_num))

        avg_val = sum(color)/len(color)

        if avg_val < 250:
            is_white = False
            break

    return is_white


def img_bottom_margin(img: Image.Image) -> Image.Image:
    w, h = img.size

    current_margin = 0
    for y in reversed(range(h)):
        if is_line_white(img, w, y):
            current_margin += 1
        else:
            break

    proper_height = h - current_margin + BOTTOM_MARGIN

    if proper_height < h:
        img = img.crop((0, 0, w, proper_height))

    if proper_height > h:
        border = proper_height - h
        img = ImageOps.expand(img, border, (255, 255, 255))
        img = img.crop((border, border, w+border, proper_height+border))

    return img


@ click.command()
@ click.argument("args", nargs=-1)
def cli(args):
    # click.echo("List of cropped images:")

    img_paths = [validate_image(arg) for arg in args if validate_image(arg) is not None]

    for p in img_paths:
        img = Image.open(p)  # type: Image.Image
        img = img_fit(img)
        img = img_bottom_margin(img)
        img.save(fp=p, quality=100)

    # click.confirm('♥')


def test():
    cli(['Y:\\Python\\PyFitWidthAndCropBottom\\test740.jpg'])


if getattr(sys, "frozen", False):
    cli()
else:
    # tests are run only if app is not frozen
    test()
    pass
