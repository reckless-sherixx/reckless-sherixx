import xml.etree.ElementTree as ET

from scripts.make_info_card import render_info_card


def test_card_contains_only_approved_identity_copy():
    svg = render_info_card()
    ET.fromstring(svg)
    for text in (
        "Vidyansh Singh",
        "Open Source Contributor · Kubernetes · Go",
        "Cloud Native and Distributed Systems",
        "Go · Kubernetes · TypeScript · Docker",
    ):
        assert text in svg
    assert "Open Source Developer" not in svg
    assert "employed at" not in svg.lower()


def test_card_animation_is_one_shot():
    svg = render_info_card()
    assert "@keyframes lineIn" in svg
    assert "infinite" not in svg


def test_static_card_has_no_animation():
    assert "@keyframes" not in render_info_card(static=True)
