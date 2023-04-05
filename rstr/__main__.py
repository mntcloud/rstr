import argparse
import math

from PIL import Image, ImageDraw

parser = argparse.ArgumentParser(
    prog="rstr",
    description="rasterize your images based on brightness",
    epilog="nabobin is dead"
)

parser.add_argument('input', help="path to an image, that you want to rasterize")
parser.add_argument('output', help="path, where to store the output image")
parser.add_argument('-mt', '--maxTiles',
                    default=100, action="store", type=int,
                    help="the maximum number of tiles used in one row, defaults to 100")
parser.add_argument('-tr', '--transparent', action="store_true", help="set background to transparent")

args = parser.parse_args()

f_in_name = args.input
f_out_name = args.output

f_in = Image.open(f_in_name)
f_out = Image.new(mode="RGB", size=f_in.size, color=(255, 255, 255, 0))

fin_width = f_in.size[0]
fin_height = f_in.size[1]

# Maximum number of tiles on X-axis for squashing image
maxTilesX = args.maxTiles

# The maximum size of a tile
maxTileSize = fin_width / maxTilesX

draw_ctx = ImageDraw.Draw(f_out)

# Brief on what algorithm is doing:
# Using information about brightness of every pixel
# we're calculating a size of a tile
# based on maximum tile size and brightness of a pixel

# tileSize is used as the step for filling our X-axis and Y-axis
# and keep consistent on tiles size, t.i to be in form of a square
for y in range(0, f_in.height, int(maxTileSize)):
    for x in range(0, f_in.width, int(maxTileSize)):
        pixel = 0
        _p = f_in.getpixel((x, y))

        if type(_p) is tuple:
            # NOTE: https://www.w3.org/TR/AERT/#color-contrast
            pixel = 0.299 * _p[0] + 0.587 * _p[1] + 0.114 * _p[2]

            # in case if we have zero opaque,
            # set resulted pixel value to non zero
            if _p[3] == 0.0:
                pixel = 255.0
        else:
            pixel = _p

        # Brightness coefficient in a reverse range from 1 to 0
        coefficient = 1 - (float(pixel) / 255)

        # The size of a tile for drawing
        size = math.floor(coefficient * maxTileSize)

        # NOTE: sometimes aligning is failing, investigate
        center_cord = (maxTileSize / 2, maxTileSize / 2)
        upper_cord = x + center_cord[0] - (size / 2), y + center_cord[1] - (size / 2)
        lower_cord = upper_cord[0] + size, upper_cord[1] + size

        # First tuple for upper left coords, second tuple for lower-right coords
        draw_ctx.rectangle((upper_cord, lower_cord), fill=(0, 0, 0))

if args.transparent:
    f_out.save(f_out_name, "PNG", transparency=(255, 255, 255))
else:
    f_out.save(f_out_name, "PNG")
