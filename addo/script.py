import os, argparse
from logging.config import fileConfig
from ConfigParser import SafeConfigParser
from .legacy_parser import LegacyParser
from render import FileRenderer


def main():
    """
    Commandline implementation of Addo. Performs commandline and config file parsing, initialises the renderer and
    parser, and then hands off control.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument('ini_filename', metavar='config file',
                        help='A config file instead of commandline parameters')
    parser.add_argument('-d', dest='destinations',
                        help='The file containing the destinations XML')
    parser.add_argument('-t', dest='taxonomy',
                        help='The file containing the taxonomy XML')
    parser.add_argument('-r', dest='template',
                        help='The file containing the template to be rendered')
    parser.add_argument('-o', dest='output',
                        help='The directory to output the rendered HTML')
    parser.add_argument('--debug', dest='debug', action='store_true',
                        help='Be verbose. This allows errors to be output as they occur.')
    args = parser.parse_args()

    config = {}
    if args.ini_filename:
        config_parser = SafeConfigParser()
        config_parser.read([args.ini_filename])
        ini_fullpath = os.path.abspath(args.ini_filename)
        ini_dir = os.path.dirname(ini_fullpath)
        # Initialise python logging module
        if config_parser.has_section('loggers'):
            fileConfig(ini_fullpath, dict(__file__=ini_fullpath, here=ini_dir))
        # Extract Addo specific config
        for element in config_parser:
            if element[0:5] == 'addo.':
                config[element[5:]] = config_parser[element].format(here=ini_dir)

    for name, value in args.items():
        if value is not None:
            config[name] = value
    try:
        destinations_file_handle = open(config['destinations'], 'rb')
        taxonomy_file_handle = open(config['destinations'], 'rb')
        template_file_handle = open(config['destinations'], 'rb')
        if not os.path.isdir(config['output']):
            parser.error('Invalid output directory')
    except KeyError, e:
        parser.error('`%s` is missing from the configuration. Check the config file or your commandline parameters' % e)
    except IOError, e:
        parser.error(str(e))

    try:
        destination_parser = LegacyParser(source=destinations_file_handle,
                                          taxonomy=taxonomy_file_handle)
        renderer = FileRenderer(template_file_handle)
        for destination in destination_parser.destinations():
            renderer.render(destination)
    except Exception, e:
        if args.debug:
            raise
        parser.exit(4, str(e))



