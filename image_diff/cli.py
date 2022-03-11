import click
from click_default_group import DefaultGroup
from PIL import Image, ImageChops
import io
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
    first_img = Image.open(first)
    second_img = Image.open(second)
    diff = ImageChops.difference(first_img, second_img)
    if output == "-":
        buffer = io.BytesIO()
        diff.save(buffer, "PNG")
        sys.stdout.buffer.write(buffer.getvalue())
    else:
        diff.save(output)
