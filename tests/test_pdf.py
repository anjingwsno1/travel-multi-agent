import unittest

from tools.pdf import format_inline


class TravelPdfTests(unittest.TestCase):
    def test_converts_bold_markdown_to_reportlab_markup(self) -> None:
        self.assertEqual(format_inline("**上海** & <外滩>"), "<b>上海</b> &amp; &lt;外滩&gt;")
