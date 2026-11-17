"""Tests for the resumable AI sprite-sheet pipeline.

Run: py -3.12 -E -W ignore::ResourceWarning -m unittest discover -s tools -p test_pixeldrive.py
"""
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

import gen_pixeldrive as drive


class PixelDriveTests(unittest.TestCase):
    def test_progress_reports_planned_roster_before_a_run_starts(self):
        expected = len(drive.worklist())
        with tempfile.TemporaryDirectory() as root:
            px = os.path.join(root, "pixelai")
            output = StringIO()
            with patch.object(drive.ps, "PX", px), patch.object(drive.ps, "PROG", os.path.join(px, "progress")), \
                    patch.object(drive, "SHEETS", os.path.join(px, "sheets")), redirect_stdout(output):
                drive.progress()

            self.assertTrue(os.path.isdir(os.path.join(px, "sheets")))
            self.assertIn("0 of %d planned" % expected,
                          open(os.path.join(px, "PROGRESS.md"), encoding="utf-8").read())
            self.assertIn("0 of %d planned" % expected, output.getvalue())


if __name__ == "__main__":
    unittest.main()
