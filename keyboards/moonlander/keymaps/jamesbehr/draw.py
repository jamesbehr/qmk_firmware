import json
import argparse
from typing import List, Union, Dict, Any
from dataclasses import dataclass
import xml.etree.ElementTree

GREY = "#ececec"
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
            elif isinstance(child, xml.etree.ElementTree.Element):
                element.append(child)
            else:
                element.append(child.xml())

        return element

    def render_xml(self):
        tree = self.xml()
        xml.etree.ElementTree.indent(tree)
        return xml.etree.ElementTree.tostring(tree, encoding="unicode")


def el(element, *children, **props):
    return Element(element, children, props)


def Embed(*, path, x, y, w, h):
    with open(path, "r") as svg:
        return el(
            "svg",
            xml.etree.ElementTree.parse(svg).getroot(),
            xmlns="http://www.w3.org/2000/svg",
            x=x,
            y=y,
            width=w,
            height=h,
        )


def Key(*, svg=None, text=None, color=GREY, x, y, w=1, h=1, ghosted, matrix):
    width = SIZE * w
    height = SIZE * h
    inner_border_size = max(INNER_OFFSET_X, INNER_OFFSET_Y) * 2
    inner_width = width - INNER_OFFSET_X * 2
    inner_height = height - INNER_OFFSET_Y * 2
    inner_style = {
        "fill": color,
        "stroke-width": BORDER_SIZE,
    }

    if svg is not None:
        icon_size = 25
        child = Embed(
            path=svg,
            x=INNER_OFFSET_X + (inner_width - icon_size) / 2,
            y=INNER_OFFSET_Y + (inner_height - icon_size) / 2,
            w=icon_size,
            h=icon_size,
        )

    if text is not None:
        text_style = {
            "font-size": "16px",
            "color": "#272727",
            "font-family": "'Helvetica', 'Arial', sans-serif",
            "text-anchor": "middle",
            "dominant-baseline": "middle",
        }

        child = el(
            "text",
            text,
            style=text_style,
            x=INNER_OFFSET_X + inner_width / 2,
            y=INNER_OFFSET_Y + inner_height / 2,
        )

    if ghosted:
        return el(
            "g",
            el(
                "rect",
                fill=color,
                rx=BORDER_RADIUS,
                width=width,
                height=height,
            ),
            el(
                "rect",
                stroke_width=BORDER_SIZE,
                stroke="#272727",
                fill="rgba(0,0,0,0.15)",
                rx=BORDER_RADIUS,
                width=width,
                height=height,
            ),
            transform=f"translate({x * SIZE}, {y * SIZE})",
        )

    return el(
        "g",
        el(
            "rect",
            rx=BORDER_RADIUS,
            fill=color,
            width=width,
            height=height,
        ),
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
        child,
        transform=f"translate({x * SIZE}, {y * SIZE})",
    )


def keys(layout, layer, labels):
    for n, layout_props in enumerate(layout):
        keycode = layer[n]

        label_props = labels.get(keycode, keycode)
        if isinstance(label_props, str):
            label_props = {"text": label_props}

        del layout_props["label"]

        props = {
            **layout_props,
            **label_props,
            "ghosted": keycode in ("KC_NO", "KC_TRNS"),
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
                el("stop", offset="0%", stop_color="rgba(255,255,255,0.2)"),
                el("stop", offset="100%", stop_color="rgba(0,0,0,0.15)"),
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
