import json
import argparse
from typing import List, Union, Dict, Any
from dataclasses import dataclass
import xml.etree.ElementTree


parser = argparse.ArgumentParser(description="Render QMK keymap to SVG")
parser.add_argument("--info", type=argparse.FileType("r"), help="QMK info JSON")
parser.add_argument("--keymap", type=argparse.FileType("r"), help="QMK keymap JSON")
parser.add_argument(
    "--labels",
    type=argparse.FileType("r"),
    help="Mapping of QMK symbol names to string labels",
)
parser.add_argument("--layer", type=int, help="Integer index of the layer to export")
args = parser.parse_args()


def attribute(key):
    return key.replace("_", "-")


def attribute_value(name, value):
    if name == "style":
        return ";".join(f"{k}:{v}" for k, v in value.items())

    return str(value)


@dataclass
class Element:
    element: str
    children: List[Union[str, "Element"]]
    props: Dict[str, Any]

    def xml(self):
        attributes = {
            attribute(k): attribute_value(k, v) for k, v in self.props.items()
        }
        element = xml.etree.ElementTree.Element(self.element, attributes)
        for child in self.children:
            if isinstance(child, str):
                if element.text is not None:
                    raise RuntimeError("multiple text children not supported")

                element.text = child
            else:
                element.append(child.xml())

        return element

    def render_xml(self):
        # TODO: Render to string not stdout
        xml.etree.ElementTree.dump(self.xml())


def el(element, *children, **props):
    return Element(element, children, props)


def Key(*, label, x, y, w=1, h=1, ghosted, matrix):
    size = 54
    border_size = 1
    border_radius = 5
    inner_offset_x = 6
    inner_offset_y = 3
    inner_border_size = max(inner_offset_x, inner_offset_y) * 2

    outer_style = {
        "fill": "#ccc",
        "stroke-width": border_size,
        "stroke": "#000",
    }

    inner_style = {
        "fill": "rgba(255,255,255,0.8)",
        "stroke-width": border_size,
        "stroke": "rgba(0,0,0,.1)",
    }

    text_style = {
        "font-size": "12px",
        "font-family": "'Helvetica', 'Arial', sans-serif",
    }

    width = size * w
    height = size * h
    inner_width = width - inner_offset_x * 2
    inner_height = height - inner_offset_y * 2

    if ghosted:
        return el(
            "g",
            el("rect", style=outer_style, rx=border_radius, width=width, height=height),
            transform=f"translate({x * size}, {y * size})",
        )

    return el(
        "g",
        el("rect", style=outer_style, rx=border_radius, width=width, height=height),
        el(
            "rect",
            style=inner_style,
            rx=border_radius,
            x=inner_offset_x,
            y=inner_offset_y,
            width=width - inner_border_size,
            height=height - inner_border_size,
        ),
        el(
            "text",
            label,
            alignment_baseline="middle",
            text_anchor="middle",
            style=text_style,
            x=inner_offset_x + inner_width / 2,
            y=inner_offset_y + inner_height / 2,
        ),
        transform=f"translate({x * size}, {y * size})",
    )


def keys(layout, layer, labels):
    for n, layout_props in enumerate(layout):
        keycode = layer[n]

        props = {
            **layout_props,
            "ghosted": keycode in ("KC_NO", "KC_TRNS"),
            "label": labels.get(keycode, keycode),
        }

        yield Key(**props)


def Keyboard(layout, layer, labels):
    # TODO: Determine width and height
    return el(
        "svg",
        *keys(layout, layer, labels),
        width=1000,
        height=420,
        xmlns="http://www.w3.org/2000/svg",
    )


info = json.load(args.info)
keymap = json.load(args.keymap)
labels = json.load(args.labels)

layout_name = keymap["layout"]
layout = info["layouts"][layout_name]["layout"]

tree = Keyboard(layout, keymap["layers"][args.layer], labels)
tree.render_xml()
