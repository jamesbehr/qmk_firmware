import json
import argparse
from typing import List, Union, Dict, Any
from dataclasses import dataclass
import xml.etree.ElementTree

OUTER_SIZE = 54
BORDER_SIZE = 2
SIZE = 54 - BORDER_SIZE * 2
BORDER_RADIUS = 5
INNER_OFFSET_X = 3
INNER_OFFSET_Y = 3


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
        tree = self.xml()
        xml.etree.ElementTree.indent(tree)
        return xml.etree.ElementTree.tostring(tree, encoding="unicode")


def el(element, *children, **props):
    return Element(element, children, props)


def Key(*, label, x, y, w=1, h=1, ghosted, matrix):
    width = SIZE * w
    height = SIZE * h

    if ghosted:
        return el(
            "g",
            el(
                "rect",
                stroke_width=BORDER_SIZE,
                stroke="#272727",
                fill="#ccc",
                rx=BORDER_RADIUS,
                width=width,
                height=height,
            ),
            transform=f"translate({x * SIZE}, {y * SIZE})",
        )

    inner_border_size = max(INNER_OFFSET_X, INNER_OFFSET_Y) * 2
    inner_width = width - INNER_OFFSET_X * 2
    inner_height = height - INNER_OFFSET_Y * 2
    inner_style = {
        "fill": "#ececec",
        "stroke-width": BORDER_SIZE,
    }

    text_style = {
        "font-size": "14px",
        "color": "#272727",
        "font-family": "'Helvetica', 'Arial', sans-serif",
        "text-anchor": "middle",
        "dominant-baseline": "middle",
    }

    return el(
        "g",
        el(
            "rect",
            rx=BORDER_RADIUS,
            stroke_width=BORDER_SIZE,
            stroke="#272727",
            fill="url(#keycap-border)",
            width=width,
            height=height,
        ),
        el(
            "rect",
            style=inner_style,
            rx=BORDER_RADIUS,
            x=INNER_OFFSET_X,
            y=INNER_OFFSET_Y,
            width=width - inner_border_size,
            height=height - inner_border_size,
        ),
        el(
            "text",
            label,
            # alignment_baseline="middle",
            # text_anchor="middle",
            style=text_style,
            x=INNER_OFFSET_X + inner_width / 2,
            y=INNER_OFFSET_Y + inner_height / 2,
        ),
        transform=f"translate({x * SIZE}, {y * SIZE})",
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
    width = max(props.get("w", 1) + props["x"] for props in layout)
    height = max(props.get("h", 1) + props["y"] for props in layout)

    return el(
        "svg",
        el(
            "defs",
            el(
                "linearGradient",
                el("stop", offset="0%", stop_color="#fefefe"),
                el("stop", offset="100%", stop_color="#c4c4c4"),
                id="keycap-border",
                x1="0%",
                y1="0%",
                x2="0%",
                y2="100%",
            ),
        ),
        *keys(layout, layer, labels),
        width=width * SIZE + BORDER_SIZE,
        height=height * SIZE + BORDER_SIZE,
        xmlns="http://www.w3.org/2000/svg",
    )


info = json.load(args.info)
keymap = json.load(args.keymap)
labels = json.load(args.labels)

layout_name = keymap["layout"]
layout = info["layouts"][layout_name]["layout"]

tree = Keyboard(layout, keymap["layers"][args.layer], labels)
print(tree.render_xml())
