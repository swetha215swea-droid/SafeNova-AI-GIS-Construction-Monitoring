
import numpy as np
from PIL import Image, ImageChops


def calculate_change_percentage(before, after):
    """Calculate the percentage of pixels that differ."""
    before = before.convert("RGB")
    after = after.convert("RGB").resize(before.size)

    difference = np.array(
        ImageChops.difference(before, after)
    )

    changed_pixels = np.any(difference > 30, axis=2)

    return changed_pixels.mean() * 100


def test_identical_images_have_no_change():
    image = Image.new("RGB", (10, 10), "white")

    result = calculate_change_percentage(image, image)

    assert result == 0.0


def test_different_images_show_change():
    before = Image.new("RGB", (10, 10), "white")
    after = Image.new("RGB", (10, 10), "black")

    result = calculate_change_percentage(before, after)

    assert result == 100.0


def test_result_is_between_zero_and_hundred():
    before = Image.new("RGB", (10, 10), "white")
    after = Image.new("RGB", (10, 10), "white")
    after.putpixel((0, 0), (0, 0, 0))

    result = calculate_change_percentage(before, after)

    assert 0 <= result <= 100
