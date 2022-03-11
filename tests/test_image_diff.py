from click.testing import CliRunner
from image_diff.cli import cli
from PIL import Image
import json
import pytest


def test_version():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert result.output.startswith("cli, version ")


@pytest.mark.parametrize(
    "input,error",
    (
        ({}, "JSON must be a list of lists"),
        ([{}], "Row 0 is not a list"),
        ([[{}]], "Cell in row 0 is not a [0, 0, 0]"),
        ([[[0]]], "Cell in row 0 is not a [0, 0, 0]"),
        ([[[0, 0]]], "Cell in row 0 is not a [0, 0, 0]"),
        ([[[0, 0, 0]], []], "Row 1 is not the expected length of 1"),
    ),
)
def test_compile_validation(input, error):
    runner = CliRunner()
    with runner.isolated_filesystem():
        open("test.json", "w").write(json.dumps(input))
        result = runner.invoke(cli, ["compile", "test.json"])
        assert result.exit_code == 1
        assert result.output.strip() == "Error: {}".format(error)


def test_compile():
    runner = CliRunner()
    with runner.isolated_filesystem():
        open("test.json", "w").write(
            json.dumps([[[0, 0, 0], [255, 0, 0]], [[255, 0, 0], [0, 0, 0]]])
        )
        result = runner.invoke(cli, ["compile", "test.json", "-o", "out.png"])
        assert result.exit_code == 0
        png = Image.open("out.png")
        assert list(png.getdata()) == [(0, 0, 0), (255, 0, 0), (255, 0, 0), (0, 0, 0)]


def test_diff():
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Write out two test images
        runner.invoke(
            cli,
            ["compile", "-", "-o", "one.png"],
            input=json.dumps([[[0, 0, 0], [0, 0, 0]], [[255, 0, 0], [0, 0, 0]]]),
        )
        runner.invoke(
            cli,
            ["compile", "-", "-o", "two.png"],
            input=json.dumps([[[0, 0, 0], [255, 0, 0]], [[255, 0, 0], [0, 0, 0]]]),
        )

        result = runner.invoke(cli, ["diff", "one.png", "two.png", "-o", "diff.png"])
        assert result.exit_code == 0, result.output
        png = Image.open("diff.png")
        assert list(png.getdata()) == [
            (0, 0, 0, 0),
            (0, 0, 0, 0),
            (255, 0, 0, 0),
            (0, 0, 0, 0),
        ]
