from unittest import TestCase
from addo.render import prettify_paragraphs, FileRenderer


class TestParagraphPrettify(TestCase):
    def test_split_into_p(self):
        result = prettify_paragraphs('Par1\n\nPar2\n\nPar3')
        self.assertEqual(result.count('<p>'), 3)
        self.assertEqual(result.count('</p>'), 3)

    def test_split_only_double(self):
        result = prettify_paragraphs('Par1\nPar2\n\nPar3')
        self.assertEqual(result.count('<p>'), 2)
        self.assertEqual(result.count('</p>'), 2)

    def test_split_multiple(self):
        """Test if there is multiple line-breaks"""
        result = prettify_paragraphs('Par1\n\nPar2\n\n\nPar3')
        self.assertEqual(result.count('<p>'), 3)
        self.assertEqual(result.count('</p>'), 3)

    def test_split_multiple_joined(self):
        """Test if there is multiple line-breaks, more than 2"""
        result = prettify_paragraphs('Par1\n\nPar2\n\n\n\nPar3')
        self.assertEqual(result.count('<p>'), 3)
        self.assertEqual(result.count('</p>'), 3)

    def test_bold_small_paragraphs(self):
        """Test if there is multiple line-breaks, more than 2"""
        paragraph = """
        A sent wrapper fishes across a bog. Inside the shower suffers the confining twin.

        Par2

        When can the constitutional glance the linguistic life? An error participates after the ballot.
        """

        result = prettify_paragraphs(paragraph)
        self.assertEqual(result.count('<p>'), 3)
        self.assertEqual(result.count('</p>'), 3)
        self.assertEqual(result.count('<b>Par2</b>'), 1, msg='Could not find <b> paragraph.')


class TestRenderGlobals(TestCase):
    """This is more of an integration test, but we do not need to unittest Mako, just our insertion of some globals

    If Addo was expanded to include all of Mako's functionality, we would need to do this, as we would insert
    global using Mako's own framework for doing so.
    """
    def test_prettify_paragraphs(self):
        template = FileRenderer(text='${prettify_paragraphs(test_data)}')
        result = template.render_unicode(test_data='Some Data')
        self.assertEqual(result, '<p><b>Some Data</b></p>')