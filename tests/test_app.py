
from PIL import Image
from image_utils import calculate_change_percentage


def test_identical_images_have_no_change():
    image = Image.new("RGB", (10, 10), "white")
    assert calculate_change_percentage(image, image) == 0.0


def test_different_images_show_change():
    before = Image.new("RGB", (10, 10), "white")
    after = Image.new("RGB", (10, 10), "black")
    assert calculate_change_percentage(before, after) == 100.0


def test_result_is_between_zero_and_hundred():
    before = Image.new("RGB", (10, 10), "white")
    after = Image.new("RGB", (10, 10), "white")
    after.putpixel((0, 0), (0, 0, 0))

    result = calculate_change_percentage(before, after)
    assert 0 <= result <= 100
