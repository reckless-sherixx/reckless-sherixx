import xml.etree.ElementTree as ET

from PIL import Image

from scripts.make_ascii_svg import image_to_ascii_rows, render_ascii_svg
from scripts.prep_photo import prepare_portrait


def test_image_to_ascii_rows_maps_white_to_spaces_and_black_to_dense_glyphs():
    image = Image.new("L", (2, 1), 255)
    image.putpixel((1, 0), 0)
    rows = image_to_ascii_rows(image, cols=2, rows=1)
    assert rows[0][0] == " "
    assert rows[0][1] == "@"


def test_prepare_portrait_outputs_grayscale_with_white_background(tmp_path):
    source = tmp_path / "source.png"
    output = tmp_path / "prepared.png"
    Image.new("RGB", (8, 8), "gray").save(source)

    def fake_remove(image):
        cutout = Image.new("RGBA", image.size, (0, 0, 0, 0))
        cutout.paste((64, 64, 64, 255), (2, 2, 6, 6))
        return cutout

    assert prepare_portrait(source, output, fake_remove) == (8, 8)
    prepared = Image.open(output)
    assert prepared.mode == "L"
    assert prepared.getpixel((0, 0)) == 255
    assert prepared.getpixel((4, 4)) < 255


def test_render_ascii_svg_is_valid_and_identified():
    svg = render_ascii_svg([" @", "@@"])
    ET.fromstring(svg)
    assert "reckless-sherixx@github" in svg
    assert "Vidyansh Singh" in svg
    assert "repeatCount=\"indefinite\"" not in svg
    assert "clipPath" in svg


def test_static_portrait_has_no_smil_animation():
    assert "<animate" not in render_ascii_svg(["@@"], static=True)
