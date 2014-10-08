"""Contains the method used to run the generator from the command-line."""

import os, argparse, codecs
from logging import getLogger, basicConfig
from logging.config import fileConfig
from ConfigParser import SafeConfigParser
from .legacy_parser import LegacyParser
from render import FileRenderer


def get_args_parser():
    """Initialises and returns the CLI opts parser"""
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument('ini_filename', metavar='config file', nargs='?',
                        help='A config file instead of commandline parameters')
    parser.add_argument('-d', dest='destinations',
                        help='The file containing the destinations XML')
    parser.add_argument('-t', dest='taxonomy',
                        help='The file containing the taxonomy XML')
    parser.add_argument('-r', dest='template',
                        help='The file containing the template to be rendered')
    parser.add_argument('--tmp', dest='temp_dir',
                        help='A directory to put temporary files into')
    parser.add_argument('-o', dest='output',
                        help='The directory to output the rendered HTML')
    parser.add_argument('--debug', dest='debug', action='store_true',
                        help='Be verbose. This allows errors to be output as they occur.')
    return parser


def get_ini_config(ini_filename, section, ini_fp=None):
    """Extract config from an ini file named in ``ini_filename``, from the ``section`` provided.
    Configure logging on the way past.

    ``ini_fp`` if provided is used to read the configuration, instead of opening the file. Pass this if the
    file has been opened for some other reason, to save re-opening it.
    """
    ini_fullpath = os.path.abspath(ini_filename)
    ini_dir = os.path.dirname(ini_fullpath)
    config_parser = SafeConfigParser({'here': ini_dir})
    if ini_fp:
        config_parser.readfp(ini_fp)
    else:
        config_parser.read([ini_fullpath])

    # Initialise python logging module
    if config_parser.has_section('loggers'):
        fileConfig(ini_fullpath, dict(__file__=ini_fullpath, here=ini_dir))

    # Extract Addo specific config
    if config_parser.has_section(section):
        return {name: value for name, value in config_parser.items(section)}
    else:
        return {}


def main(args=None):
    """
    Commandline implementation of Addo. Transforms the given destinations into HTML using the given template.
    """
    parser = get_args_parser()
    args = parser.parse_args(args)

    if args.ini_filename:
        config = get_ini_config(args.ini_filename, 'addo')
    else:
        config = {}
        basicConfig()  # Configure Logging, as there is no config file to do it from.

    # Copy the CLI config into the config dict
    for name, value in vars(args).items():
        if value is not None:
            config[name] = value

    # Check for required config
    if 'destinations' not in config:
        parser.error('Missing `destinations` parameter.')
    if 'taxonomy' not in config:
        parser.error('Missing `destinations` parameter.')
    if 'output' not in config:
        parser.error('Missing `output` parameter.')
    if not os.path.isdir(config['output']):
        parser.error('Invalid output directory')

    if 'template' not in config:
        config['template'] = os.path.join(os.path.dirname(__file__), 'template.html')
    if not os.path.isfile(config['template']):
        parser.error('Invalid template file')

    try:
        destinations_fp = open(config['destinations'], 'rb')
        taxonomy_fp = open(config['taxonomy'], 'rb')
    except IOError, e:
        parser.error(str(e))

    log = getLogger('addo.script')
    try:
        destination_parser = LegacyParser(source=destinations_fp,
                                          taxonomy=taxonomy_fp)
        if 'temp_dir' in config:
            renderer = FileRenderer(filename=config['template'], module_directory=config['temp_dir'])
        else:
            log.warn('No temporary dir for templating. Performance will be greatly decreased.')
            renderer = FileRenderer(filename=config['template'])

        rendered = 0
        for destination in destination_parser.destinations():
            output_filename = os.path.join(config['output'], '%s.html' % destination.name)
            with codecs.open(output_filename, 'wb', encoding='UTF-8') as output_handle:
                log.info('Rendering %s' % destination.name)
                output_handle.write(renderer.render_unicode(parser=destination_parser,
                                                            destination=destination))
            rendered += 1
    except Exception, e:
        # Show the raw exception to the user if debugging
        if args.debug:
            raise
        # Show the exception string otherwise
        parser.exit(4, '%s\n' % e)

    print 'Rendered %d files.' % rendered

