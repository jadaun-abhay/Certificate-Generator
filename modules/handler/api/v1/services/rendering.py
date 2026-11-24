from PIL import Image, ImageDraw, ImageFont

from modules.handler.choices import Alignment
from modules.handler.models import TemplateField

# anchor values: https://pillow.readthedocs.io/en/stable/handbook/text-anchors.html
_ANCHOR_BY_ALIGNMENT = {
    Alignment.LEFT: "lm",
    Alignment.CENTER: "mm",
    Alignment.RIGHT: "rm",
}


def _fit_font(font_path: str, text: str, box_width: int, box_height: int) -> ImageFont.FreeTypeFont:
    """Return the largest font (capped by the box height) that fits `text`
    inside a `box_width` x `box_height` box."""
    size = max(box_height, 1)
    font = ImageFont.truetype(font_path, size)
    while size > 1:
        left, top, right, bottom = font.getbbox(text)
        if (right - left) <= box_width and (bottom - top) <= box_height:
            break
        size -= 1
        font = ImageFont.truetype(font_path, size)
    return font


def render_fields(
    template_image: Image.Image,
    fields: list[TemplateField],
    row: dict[str, str],
    default_font_path: str,
) -> Image.Image:
    """Draw every field in `fields` onto a copy of `template_image` using the
    values in `row` (keyed by `TemplateField.field_name`), returning the
    composited image. Fields missing from `row` are silently skipped.
    """
    image = template_image.copy()
    draw = ImageDraw.Draw(image)

    for field in fields:
        text = row.get(field.field_name)
        if text is None or text == "":
            continue

        box_width = field.bottom_right_x - field.top_left_x
        box_height = field.bottom_right_y - field.top_left_y
        font_path = field.font.file.path if field.font_id else default_font_path
        font = _fit_font(font_path, str(text), box_width, box_height)

        center_y = (field.top_left_y + field.bottom_right_y) // 2
        if field.alignment == Alignment.LEFT:
            position = (field.top_left_x, center_y)
        elif field.alignment == Alignment.RIGHT:
            position = (field.bottom_right_x, center_y)
        else:
            position = (
                (field.top_left_x + field.bottom_right_x) // 2,
                center_y,
            )

        draw.text(
            position,
            str(text),
            fill=field.text_color,
            font=font,
            anchor=_ANCHOR_BY_ALIGNMENT[field.alignment],
        )

    return image
