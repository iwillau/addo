"""Provides the FileRenderer class, a (very) simple override of Mako's Template class. Also some small helper functions
for the template rendering."""

from mako.template import Template


def prettify_paragraphs(source):
    """
    Performs some simple transformations on a large-ish body of text to make it easier to mark-up in HTML.

    1. For any grouping of text that has two newlines, it wraps this group in <p> tags.
    2. If an entire paragraph is less than 40 characters, it wraps it in <b> tags (implied subheading)

    :param source:
    :return:
    """
    paragraphs = []
    for paragraph in source.split('\n\n'):
        if len(paragraph.strip()) == 0:
            continue
        if len(paragraph) < 40:
            paragraphs.append(u'<b>%s</b>' % paragraph.strip())
        else:
            paragraphs.append(paragraph)

    return ''.join([u'<p>%s</p>' % p for p in paragraphs])


class FileRenderer(Template):
    def render_unicode(self, *args, **data):
        """
        Inserts render helpers, not configurable in any way. Then calls the super method from the Mako Template
        class.
        """
        data['prettify_paragraphs'] = prettify_paragraphs
        return super(FileRenderer, self).render_unicode(*args, **data)

