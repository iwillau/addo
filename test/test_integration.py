import os, shutil, tempfile
from addo.script import main
from unittest import TestCase

TEST_TAXONOMY = """<?xml version="1.0" encoding="utf-8"?>
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

TEST_DESTINATION = """<?xml version="1.0" encoding="utf-8"?>
<destinations>
 <destination atlas_id="111222" asset_id="1-1" title="Africa" title-ascii="Africa">
  <random><![CDATA[Random String goes here ]]></random>
 </destination>
 <destination atlas_id="111333" asset_id="2-1" title="South Africa" title-ascii="South Africa">
  <random><![CDATA[Random String goes here ]]></random>
 </destination>
</destinations>
"""

TEST_TEMPLATE = """DESTINATION: ${destination.title}"""


class TestIntegrationScript(TestCase):

    def join(self, *children):
        """Join some paths together to the root"""
        return os.path.abspath(os.path.join(self.path, *children))

    def setUp(self):
        self.path = tempfile.mkdtemp()
        os.mkdir(self.join('output'))
        with open(self.join('taxonomy.xml'), 'wb') as fh:
            fh.write(TEST_TAXONOMY)
        with open(self.join('destinations.xml'), 'wb') as fh:
            fh.write(TEST_DESTINATION)

    def tearDown(self):
        shutil.rmtree(self.path)

    def test_missing_template_file(self):
        with self.assertRaises(SystemExit):
            main(args=['-t', self.join('taxonomy.xml'),
                       '-d', self.join('destinations.xml'),
                       '-r', self.join('template.html'),
                       '-o', self.join('output')])

    def test_missing_destinations_file(self):
        with self.assertRaises(SystemExit):
            main(args=['-t', self.join('wrong.xml'),
                       '-d', self.join('destinations.xml'),
                       '-o', self.join('output')])

    def test_missing_taxonomy_file(self):
        with self.assertRaises(SystemExit):
            main(args=['-t', self.join('taxonomy.xml'),
                       '-d', self.join('wrong.xml'),
                       '-o', self.join('output')])

    def test_file_per_destination(self):
        main(args=['-t', self.join('taxonomy.xml'),
                   '-d', self.join('destinations.xml'),
                   '-o', self.join('output')])
        self.assertEqual(len(os.listdir(self.join('output'))), 2, msg="Invalid number of generated files")

    def test_template_cache_dir(self):
        os.mkdir(self.join('tmp'))
        main(args=['-t', self.join('taxonomy.xml'),
                   '-d', self.join('destinations.xml'),
                   '--tmp', self.join('tmp'),
                   '-o', self.join('output')])
        self.assertEqual(len(os.listdir(self.join('output'))), 2, msg="Invalid number of generated files")

    def test_with_builtin_template(self):
        main(args=['-t', self.join('taxonomy.xml'),
                   '-d', self.join('destinations.xml'),
                   '-o', self.join('output')])
        self.assertTrue(os.path.isfile(self.join('output', 'africa.html')), msg="Missing file for destination")
        self.assertTrue(os.path.isfile(self.join('output', 'south_africa.html')), msg="Missing file for destination")
        self.assertTrue(os.path.getsize(self.join('output', 'africa.html')) > 1000,
                        msg="File is too small for default template")
        self.assertTrue(os.path.getsize(self.join('output', 'south_africa.html')) > 1000,
                        msg="File is too small for default template")

    def test_with_override_template(self):
        """Check that the override template is adhered to"""
        with open(self.join('template.html'), 'wb') as fh:
            fh.write(TEST_TEMPLATE)
        main(args=['-t', self.join('taxonomy.xml'),
                   '-d', self.join('destinations.xml'),
                   '-o', self.join('output'),
                   '-r', self.join('template.html')])
        self.assertTrue(os.path.isfile(self.join('output', 'africa.html')), msg="Missing file for destination")
        self.assertTrue(os.path.isfile(self.join('output', 'south_africa.html')), msg="Missing file for destination")
        with open(self.join('output', 'africa.html'), 'r') as fh:
            self.assertEqual(fh.read(), 'DESTINATION: Africa')
        with open(self.join('output', 'south_africa.html'), 'r') as fh:
            self.assertEqual(fh.read(), 'DESTINATION: South Africa')

    def test_template_error(self):
        with open(self.join('template.html'), 'wb') as fh:
            fh.write('${mem')
        with self.assertRaises(SystemExit):
            main(args=['-t', self.join('taxonomy.xml'),
                       '-d', self.join('destinations.xml'),
                       '-r', self.join('template.html'),
                       '-o', self.join('output')])
        self.assertEqual(len(os.listdir(self.join('output'))), 0)

    def test_generic_debugging(self):
        with open(self.join('destinations.xml'), 'wb') as fh:
            fh.write('error>')
        with self.assertRaises(Exception):
            main(args=['-t', self.join('taxonomy.xml'),
                       '-d', self.join('destinations.xml'),
                       '--debug',
                       '-o', self.join('output')])
        self.assertEqual(len(os.listdir(self.join('output'))), 0)

TEST_INI_FILE = """
[addo]
destinations = %(here)s/destinations.xml
taxonomy = %(here)s/taxonomy.xml
output = %(here)s/output
temp_dir = %(here)s/tmp
"""

class TestIntegrationScriptIniFile(TestCase):

    def join(self, *children):
        """Join some paths together to the root"""
        return os.path.abspath(os.path.join(self.path, *children))

    def setUp(self):
        self.path = tempfile.mkdtemp()
        os.mkdir(self.join('output'))
        os.mkdir(self.join('tmp'))
        with open(self.join('taxonomy.xml'), 'wb') as fh:
            fh.write(TEST_TAXONOMY)
        with open(self.join('destinations.xml'), 'wb') as fh:
            fh.write(TEST_DESTINATION)
        with open(self.join('config.ini'), 'wb') as fh:
            fh.write(TEST_INI_FILE)

    def tearDown(self):
        shutil.rmtree(self.path)

    def test_file_per_destination(self):
        main(args=[self.join('config.ini')])
        self.assertEqual(len(os.listdir(self.join('output'))), 2, msg="Invalid number of generated files")

    def test_with_builtin_template(self):
        main(args=[self.join('config.ini')])
        self.assertTrue(os.path.isfile(self.join('output', 'africa.html')), msg="Missing file for destination")
        self.assertTrue(os.path.isfile(self.join('output', 'south_africa.html')), msg="Missing file for destination")
        self.assertTrue(os.path.getsize(self.join('output', 'africa.html')) > 1000,
                        msg="File is too small for default template")
        self.assertTrue(os.path.getsize(self.join('output', 'south_africa.html')) > 1000,
                        msg="File is too small for default template")

    def test_with_override_template(self):
        """Check that the override template is adhered to"""
        with open(self.join('template.html'), 'wb') as fh:
            fh.write(TEST_TEMPLATE)
        main(args=[self.join('config.ini'),
                   '-r', self.join('template.html')])
        self.assertTrue(os.path.isfile(self.join('output', 'africa.html')), msg="Missing file for destination")
        self.assertTrue(os.path.isfile(self.join('output', 'south_africa.html')), msg="Missing file for destination")
        with open(self.join('output', 'africa.html'), 'r') as fh:
            self.assertEqual(fh.read(), 'DESTINATION: Africa')
        with open(self.join('output', 'south_africa.html'), 'r') as fh:
            self.assertEqual(fh.read(), 'DESTINATION: South Africa')


