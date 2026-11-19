import unittest

from PIL import Image, ImageDraw

from gen_portraits import bust_crop


class BustPortraitTests(unittest.TestCase):
    def test_face_anchor_keeps_face_and_upper_body(self):
        image = Image.new("RGBA", (400, 600), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.rectangle((240, 180, 320, 280), fill=(240, 180, 130, 255))
        draw.rectangle((210, 290, 350, 390), fill=(180, 20, 40, 255))
        crop = bust_crop(image, (0.7, 0.3, 0.467))
        self.assertEqual(crop.getpixel((40, 35)), (240, 180, 130, 255))
        self.assertEqual(crop.getpixel((40, 65)), (180, 20, 40, 255))

    def test_face_at_top_edge_does_not_add_empty_padding(self):
        image = Image.new("RGBA", (400, 600), (20, 40, 80, 255))
        crop = bust_crop(image, (0.5, 0.04, 0.29))
        self.assertEqual(crop.getpixel((40, 0)), (20, 40, 80, 255))

    def test_invalid_face_anchor_is_an_error(self):
        image = Image.new("RGBA", (400, 600))
        with self.assertRaises(ValueError):
            bust_crop(image, (0.5, 0.5, 0.3))

    def test_unanchored_bust_crops_visible_top_not_empty_margins(self):
        image = Image.new("RGBA", (400, 600), (0, 0, 0, 0))
        ImageDraw.Draw(image).rectangle((100, 100, 299, 599), fill=(20, 40, 80, 255))
        crop = bust_crop(image)
        self.assertEqual(crop.getpixel((40, 0)), (20, 40, 80, 255))
        self.assertEqual(crop.getpixel((40, 79)), (20, 40, 80, 255))


if __name__ == "__main__":
    unittest.main()
