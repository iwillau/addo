from ConfigParser import NoSectionError
from StringIO import StringIO
from argparse import ArgumentParser
from unittest import TestCase
from addo.script import get_args_parser, get_ini_config, main


class ScriptConfigurationTest(TestCase):
    def test_arg_parser_object(self):
        """get_args_parser only initialises an ArgumentParser. We're only testing that it returns an ArgumentParser"""
        self.assertIsInstance(get_args_parser(), ArgumentParser)

    def test_ini_parser_empty(self):
        """An Empty ini file should return an empty config"""
        ini = ''
        config = get_ini_config('/some/location/config.ini', 'addo', ini_fp=StringIO(ini))
        self.assertEquals(config, {})

    def test_ini_parser_simple(self):
        """Test that the ini parser returns a valid single parameter"""
        ini_file = """
[addo]
parameter = value
        """
        config = get_ini_config('/some/location/config.ini', 'addo', ini_fp=StringIO(ini_file))
        self.assertIn('parameter', config)
        self.assertEqual('value', config['parameter'])

    def test_ini_parser_interpolated(self):
        """Test that the ini parser returns an interpolated value"""
        ini_file = """
[addo]
parameter = %(here)s/value
        """
        config = get_ini_config('/some/location/config.ini', 'addo', ini_fp=StringIO(ini_file))
        self.assertIn('parameter', config)
        self.assertEqual('/some/location/value', config['parameter'])

    def test_with_empty_args(self):
        """User passes no args, should fail with SystemExit"""
        with self.assertRaises(SystemExit):
            main(args=[])

    def test_with_no_destination(self):
        with self.assertRaises(SystemExit):
            main(args=['-t', 'taxonomy.xml', '-o', 'output_dir'])

    def test_with_no_taxonomy(self):
        with self.assertRaises(SystemExit):
            main(args=['-d', 'destinations.xml', '-o', 'output_dir'])

    def test_with_no_output_dir(self):
        with self.assertRaises(SystemExit):
            main(args=['-t', 'taxonomy.xml', '-d', 'destinations.xml'])

    def test_with_invalid_output_dir(self):
        with self.assertRaises(SystemExit):
            main(args=['-t', 'taxonomy.xml', '-d', 'destinations.xml', '-o', 'output_dir'])

    def test_config_logging(self):
        """Test that the ini config catches the logging values. We're not testing 'how' it configures it as that
        is done in the logging module"""
        ini_file = """
[loggers]
keys =
"""
        with self.assertRaises(NoSectionError):
            config = get_ini_config('/some/location/config.ini', 'addo', ini_fp=StringIO(ini_file))

