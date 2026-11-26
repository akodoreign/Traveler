"""Verify the main menu's visual-only row copies keep the original controls."""
import unittest

import style_main_menu as menu


class MainMenuStyleTest(unittest.TestCase):
    def test_scoped_row_copies(self):
        layout = (menu.UI / "menu_main.ui").read_bytes()
        for stock, custom in menu.ROWS:
            original = (menu.UI / "parts" / (stock + ".ui")).read_bytes()
            styled = (menu.UI / "parts" / (custom + ".ui")).read_bytes()
            for state in ("n", "g"):
                styled = menu.replace_once(
                    styled, "uiimg/bctl_" + state + ".png", "uiimg/item_" + state + ".png"
                )
            self.assertEqual(styled, original)
            self.assertEqual(layout.count(("parts/" + custom + ".ui").encode()), 1)
            self.assertNotIn(("parts/" + stock + ".ui").encode(), layout)

    def test_presentation_assets_exist(self):
        atlas = (menu.UI / "uiimg.ssg").read_text(encoding="utf-8")
        for state in ("n", "g"):
            self.assertIn('"bctl_' + state + '.png"', atlas)
        self.assertTrue((menu.UI.parent / "resource" / "efx" / "battleui" / "panel_wide.png").is_file())


if __name__ == "__main__":
    unittest.main()
