
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

    return float(changed_pixels.mean() * 100)
