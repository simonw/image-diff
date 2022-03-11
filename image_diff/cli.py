import click
from click_default_group import DefaultGroup
from PIL import Image, ImageChops
import io
import json
import sys


@click.group(
    cls=DefaultGroup,
    default="diff",
    default_if_no_args=True,
    context_settings=dict(help_option_names=["-h", "--help"]),
)
@click.version_option()
def cli():
    "CLI tool for comparing images"


@cli.command()
@click.argument("first", type=click.File("rb"))
@click.argument("second", type=click.File("rb"))
@click.option(
    "-o",
    "--output",
    type=click.Path(file_okay=True, writable=True, dir_okay=False, allow_dash=True),
    default="-",
    help="Path to save the resulting image",
)
def diff(first, second, output):
    "Generate an image representing the difference between these two images"
    first_img, second_img = _open_images(first, second)
    diff = ImageChops.difference(first_img, second_img)
    _output(diff, output)


@cli.command()
@click.argument("json_file", type=click.File("r"))
@click.option(
    "-o",
    "--output",
    type=click.Path(file_okay=True, writable=True, dir_okay=False, allow_dash=True),
    default="-",
    help="Path to save the resulting image",
)
def compile(json_file, output):
    """
    Compile and save an image based on a JSON image description

    This is mainly useful as a testing utility.

    To produce a 3x3 black image with a red center:

    \b
        [
           [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
           [[0, 0, 0], [255, 0, 0], [0, 0, 0]],
           [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        ]

    Then:

        image-diff compile image.json image.png
    """
    pixels = json.load(json_file)
    # Verify it's a 2D array with equal length rows
    try:
        assert isinstance(pixels, list), "JSON must be a list of lists"
        num_rows = len(pixels)
        num_cols = None
        for i, row in enumerate(pixels):
            assert isinstance(row, list), "Row {} is not a list".format(i)
            # Each cell must be a 3-tuple
            for cell in row:
                assert (
                    isinstance(cell, list)
                    and len(cell) == 3
                    and all(isinstance(num, int) for num in cell)
                ), "Cell in row {} is not a [0, 0, 0]".format(i)
            if num_cols is None:
                num_cols = len(row)
            else:
                assert (
                    len(row) == num_cols
                ), "Row {} is not the expected length of {}".format(i, num_cols)
    except AssertionError as e:
        raise click.ClickException(str(e))
    # Validation complete, load the image
    image = Image.new("RGB", (num_cols, num_rows))
    for i, row in enumerate(pixels):
        for j, cell in enumerate(row):
            image.putpixel((j, i), tuple(cell))
    _output(image, output)


@cli.command()
@click.argument("first", type=click.File("rb"))
@click.argument("second", type=click.File("rb"))
def count(first, second):
    "Count the number of differing pixels in two images"
    first_img, second_img = _open_images(first, second)
    diff = ImageChops.difference(first_img, second_img)
    diff_pixels = (p for p in diff.getdata() if p != (0, 0, 0, 0))
    pixel_count = sum(1 for _ in diff_pixels)
    click.echo(pixel_count)


def _open_images(first, second):
    first_img = Image.open(first)
    second_img = Image.open(second)
    if first_img.mode != "RGBA":
        first_img = first_img.convert("RGBA")
    if second_img.mode != "RGBA":
        second_img = second_img.convert("RGBA")
    return first_img, second_img


def _output(image, output):
    if output == "-":
        buffer = io.BytesIO()
        image.save(buffer, "PNG")
        sys.stdout.buffer.write(buffer.getvalue())
    else:
        image.save(output)
