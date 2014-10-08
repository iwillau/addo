from unittest import TestCase
from StringIO import StringIO
from lxml.etree import XMLSyntaxError
from addo.legacy_parser import LegacyParser, LegacyTaxonomies
from addo.destination import Destination

TAXONOMY_VALID = """<?xml version="1.0" encoding="utf-8"?>
<taxonomies>
 <taxonomy>
  <taxonomy_name>World</taxonomy_name>
  <node atlas_node_id = "111222" ethyl_content_object_id="1" geo_id = "1">
   <node_name>Africa</node_name>
   <node atlas_node_id = "111333" ethyl_content_object_id="3" geo_id = "4">
     <node_name>South Africa</node_name>
   </node>
  </node>
 </taxonomy>
</taxonomies>
"""

XML_EMPTY = """<?xml version="1.0" encoding="utf-8"?>"""

TAXONOMY_EMPTY = """<?xml version="1.0" encoding="utf-8"?>
<taxonomies></taxonomies>"""

TAXONOMY_EMPTY_SET = """<?xml version="1.0" encoding="utf-8"?>
<taxonomies>
 <taxonomy>
 </taxonomy>
</taxonomies>"""

TAXONOMY_NO_NAME = """<?xml version="1.0" encoding="utf-8"?>
<taxonomies>
 <taxonomy>
  <taxonomy_name>World</taxonomy_name>
  <node atlas_node_id = "111222" ethyl_content_object_id="1" geo_id = "1">
   <node_name>Africa</node_name>
   <node atlas_node_id = "111333" ethyl_content_object_id="3" geo_id = "4">
   </node>
  </node>
 </taxonomy>
</taxonomies>
"""

TAXONOMY_NO_ATTRIBS = """<?xml version="1.0" encoding="utf-8"?>
<taxonomies>
 <taxonomy>
  <taxonomy_name>World</taxonomy_name>
  <node>
   <node_name>Africa</node_name>
   <node>
     <node_name>South Africa</node_name>
   </node>
  </node>
 </taxonomy>
</taxonomies>
"""

DESTINATIONS_VALID = """<?xml version="1.0" encoding="utf-8"?>
<destinations>
 <destination atlas_id="111222" asset_id="1-1" title="Africa" title-ascii="Africa">
  <random><![CDATA[Random String goes here ]]></random>
 </destination>
 <destination atlas_id="111333" asset_id="2-1" title="South Africa" title-ascii="South Africa">
  <random><![CDATA[Random String goes here ]]></random>
 </destination>
</destinations>
"""

DESTINATIONS_EMPTY_SET = """<?xml version="1.0" encoding="utf-8"?>
<destinations>
</destinations>
"""

DESTINATIONS_EMPTY_CONTENT = """<?xml version="1.0" encoding="utf-8"?>
<destinations>
 <destination atlas_id="111222" asset_id="1-1" title="Africa" title-ascii="Africa"/>
</destinations>
"""

DESTINATIONS_MISSING_TITLE = """<?xml version="1.0" encoding="utf-8"?>
<destinations>
 <destination atlas_id="111222" asset_id="1-1" title-ascii="Africa"/>
</destinations>
"""

DESTINATIONS_MISSING_TITLE_ASCII = """<?xml version="1.0" encoding="utf-8"?>
<destinations>
 <destination atlas_id="111222" asset_id="1-1" title="Africa"/>
</destinations>
"""

DESTINATIONS_MISSING_ATTRIB = """<?xml version="1.0" encoding="utf-8"?>
<destinations>
 <destination title="Africa"/>
</destinations>
"""

DESTINATIONS_CLEANUP_HISTORY = """<?xml version="1.0" encoding="utf-8"?>
<destinations>
 <destination title="Africa">
 <history>
  <history>
   <history><![CDATA[Some History 1]]></history>
   <history><![CDATA[Some History 2]]></history>
  </history>
 </history>
 </destination>
</destinations>
"""

DESTINATIONS_CLEANUP_INTRODUCTION = """<?xml version="1.0" encoding="utf-8"?>
<destinations>
 <destination title="Africa">
 <introductory>
  <introduction>
   <overview><![CDATA[An Introduction]]></overview>
  </introduction>
 </introductory>
 </destination>
</destinations>
"""

DESTINATIONS_COMPLEX_CONTENT = """<?xml version="1.0" encoding="utf-8"?>
<destinations>
 <destination title="Africa">
 <section>
  <subsection_one><![CDATA[SS 1]]></subsection_one>
  <subsection_two>
    <has_a_list><![CDATA[SS 2 El 1]]></has_a_list>
    <has_a_list><![CDATA[SS 2 El 2]]></has_a_list>
    <has_a_list><![CDATA[SS 2 El 3]]></has_a_list>
    <and_something><![CDATA[A Something!]]></and_something>
  </subsection_two>
 </section>
 <another_section><![CDATA[Another Section]]></another_section>
 </destination>
</destinations>
"""


class TestLegacyTaxonomies(TestCase):
    """This doesn't do much more than just check if it parses the correct XML. If we wanted to be picky about
    different XML errors we should define a schema, and use that to validate the XML prior to passing it to
    this class.
    """
    def test_parse(self):
        taxonomies = LegacyTaxonomies()
        taxonomies.parse_xml(StringIO(TAXONOMY_VALID))
        self.assertEqual(len(taxonomies._sets), 1)
        self.assertEqual(taxonomies._sets.keys()[0], 'World')
        self.assertDictEqual(taxonomies, {
            'africa': {'atlas_node_id': 111222,
                       'children': ['south_africa'],
                       'ethyl_content_object_id': 1,
                       'geo_id': 1,
                       'name': 'Africa',
                       'parents': []},
            'south_africa': {'atlas_node_id': 111333,
                             'children': [],
                             'ethyl_content_object_id': 3,
                             'geo_id': 4,
                             'name': 'South Africa',
                             'parents': ['africa']},
            })

    def test_parse_invalid(self):
        taxonomies = LegacyTaxonomies()
        with self.assertRaises(XMLSyntaxError):
            taxonomies.parse_xml(StringIO('error>'))
        self.assertEqual(len(taxonomies), 0)

    def test_parse_empty_xml(self):
        taxonomies = LegacyTaxonomies()
        with self.assertRaises(XMLSyntaxError):
            taxonomies.parse_xml(StringIO(XML_EMPTY))
        self.assertEqual(len(taxonomies), 0)

    def test_parse_empty(self):
        taxonomies = LegacyTaxonomies()
        taxonomies.parse_xml(StringIO(TAXONOMY_EMPTY))
        self.assertEqual(len(taxonomies._sets), 0)
        self.assertEqual(len(taxonomies), 0)

    def test_parse_empty_set(self):
        taxonomies = LegacyTaxonomies()
        taxonomies.parse_xml(StringIO(TAXONOMY_EMPTY_SET))
        self.assertEqual(len(taxonomies._sets), 1)
        self.assertIsNone(taxonomies._sets.keys()[0])
        self.assertEqual(len(taxonomies), 0)

    def test_parse_missing_node_name(self):
        taxonomies = LegacyTaxonomies()
        taxonomies.parse_xml(StringIO(TAXONOMY_NO_NAME))
        self.assertEqual(len(taxonomies._sets), 1)
        self.assertEqual(len(taxonomies), 1)

    def test_parse_missing_attribs(self):
        taxonomies = LegacyTaxonomies()
        taxonomies.parse_xml(StringIO(TAXONOMY_NO_ATTRIBS))
        self.assertEqual(len(taxonomies._sets), 1)
        self.assertEqual(len(taxonomies), 2)


class TestLegacyParser(TestCase):
    """This doesn't do much more than just check if it parses the correct XML. If we wanted to be picky about
    different XML errors we should define a schema, and use that to validate the XML prior to passing it to
    this class.
    """
    maxDiff = 1000

    def test_parse_metadata(self):
        parser = LegacyParser(StringIO(DESTINATIONS_VALID))
        self.assertDictEqual(parser.metadata, {
            'africa': {
                'asset_id': '1-1',
                'name': 'africa',
                'title': 'Africa'},
            'south_africa': {
                'asset_id': '2-1',
                'name': 'south_africa',
                'title': 'South Africa'},
        })

    def test_parse_content(self):
        parser = LegacyParser(StringIO(DESTINATIONS_VALID))
        count = 0
        names = ['africa', 'south_africa']
        for destination in parser.destinations():
            self.assertIsInstance(destination, Destination)
            self.assertEqual(destination.name, names[count])
            self.assertEqual(destination.get_content('random'), 'Random String goes here')
            count += 1
        self.assertEqual(count, 2)

    def test_parse_empty_xml(self):
        with self.assertRaises(XMLSyntaxError):
            parser = LegacyParser(StringIO(XML_EMPTY))

    def test_parse_empty_destinations(self):
        parser = LegacyParser(StringIO(DESTINATIONS_EMPTY_SET))
        count = 0
        for destination in parser.destinations():
            self.assertIsInstance(destination, Destination)
            count += 1
        self.assertEqual(count, 0)

    def test_parse_empty_content(self):
        parser = LegacyParser(StringIO(DESTINATIONS_EMPTY_CONTENT))
        for destination in parser.destinations():
            self.assertIsInstance(destination, Destination)
            self.assertEqual(destination.get_content(), {})

    def test_parse_missing_title(self):
        parser = LegacyParser(StringIO(DESTINATIONS_MISSING_TITLE))
        count = 0
        for destination in parser.destinations():
            count += 1
        self.assertEqual(count, 0)

    def test_parse_missing_title_ascii(self):
        parser = LegacyParser(StringIO(DESTINATIONS_MISSING_TITLE_ASCII))
        count = 0
        for destination in parser.destinations():
            self.assertEqual(destination.name, 'africa')
            count += 1
        self.assertEqual(count, 1)

    def test_parse_missing_attrib(self):
        parser = LegacyParser(StringIO(DESTINATIONS_MISSING_ATTRIB))
        count = 0
        for destination in parser.destinations():
            self.assertEqual(destination.name, 'africa')
            count += 1
        self.assertEqual(count, 1)

    def test_resolve_parents(self):
        parser = LegacyParser(StringIO(DESTINATIONS_VALID), StringIO(TAXONOMY_VALID))
        parents = [[], ['africa']]
        count = 0
        for destination, check_parents in zip(parser.destinations(), parents):
            for parent, check in zip(destination.parents(), check_parents):
                self.assertEqual(parent['name'], check)
                count += 1
        self.assertEqual(count, 1)

    def test_resolve_children(self):
        parser = LegacyParser(StringIO(DESTINATIONS_VALID), StringIO(TAXONOMY_VALID))
        children = [['south_africa'], []]
        count = 0
        for destination, check_children in zip(parser.destinations(), children):
            for child, check in zip(destination.children(), check_children):
                self.assertEqual(child['name'], check)
                count += 1
        self.assertEqual(count, 1)

    def test_cleanup_history(self):
        parser = LegacyParser(StringIO(DESTINATIONS_CLEANUP_HISTORY))
        count = 0
        for destination in parser.destinations():
            count += 1
            self.assertDictEqual(destination.get_content('history'), {'history': [u'Some History 1',
                                                                                  u'Some History 2']})
        self.assertEqual(count, 1)

    def test_cleanup_introduction(self):
        parser = LegacyParser(StringIO(DESTINATIONS_CLEANUP_INTRODUCTION))
        count = 0
        for destination in parser.destinations():
            count += 1
            self.assertEqual(destination.get_content('introduction'), 'An Introduction')
        self.assertEqual(count, 1)

    def test_complex_content(self):
        parser = LegacyParser(StringIO(DESTINATIONS_COMPLEX_CONTENT))
        count = 0
        for destination in parser.destinations():
            count += 1
            self.assertDictEqual(destination.get_content(),
                {'section': {
                    'subsection_one': u'SS 1',
                    'subsection_two': {'has_a_list': [u'SS 2 El 1', u'SS 2 El 2', u'SS 2 El 3'],
                                       'and_something': u'A Something!', },
                },
                 'another_section': u'Another Section',
                })
        self.assertEqual(count, 1)

