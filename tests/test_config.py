import unittest
from src.config import get_theme, Theme, global_css
from src.layout import inject_styles, enhanced_css

class TestConfig(unittest.TestCase):
    def test_get_theme(self):
        light_theme = get_theme(False)
        self.assertIsInstance(light_theme, Theme)
        self.assertEqual(light_theme.surface, "#F5F5FA")
        
        dark_theme = get_theme(True)
        self.assertIsInstance(dark_theme, Theme)
        self.assertEqual(dark_theme.surface, "#08080D")
        
    def test_css_generation(self):
        theme = get_theme(False)
        css = global_css(theme)
        self.assertIn("Inter", css)
        self.assertIn("#F5F5FA", css)
        
        encss = enhanced_css(theme)
        self.assertIn("Inter", encss)
