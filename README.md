addo
====

Static HTML generation from location metadata.

Installation
------------

Addo requires Python 2.7. It has not been tested in any other version of Python.

It is easiest to simply use pip, as in:

```bash
$ pip install git+https://github.com/iwillau/addo
```

or, alternatively:

```bash
$ git clone https://github.com/iwillau/addo
$ pip install addo
```

### Prerequisites

The above command will automatically install any prerequisites as required. This package does depend on 
[lxml](http://lxml.de/), which generally requires compilation. For unix this is a trivial procedure, for windows the 
easiest option is a binary package such as those found [here](http://www.lfd.uci.edu/~gohlke/pythonlibs/).

Usage
-----

To render a single set of destinations, with associated taxonomy into a directory of html:

```bash
$ addo -d destinations.xml -t taxonomy.xml -o output_dir
```

To specify an alternate template:

```bash
$ addo -d destinations.xml -t taxonomy.xml -r my_template.html -o output_dir
```

### Configuration
Alternately you can configure Addo using an ini file, as may be used by other Paste Deploy compatible packages. This 
would allow Addo to be embedded into another package (such as a Pyramid app).

```ini
[addo]
addo.destinations = destinations.xml
addo.taxonomy = taxonomy.xml
addo.render = my_template.html
addo.output = some_dir_somewhere
```

Which would then be used as the single parameter to the script:

```bash
$ addo myconfig.ini
```

When using the ini file, the file paths are relative to the script being run, which is probably what you want when Addo
is embedded, but if you are using addo directly, you can use Paster style semantics to specify the directory the ini
file is in:

```ini
[addo]
addo.destinations = %(here)s/destinations.xml
addo.taxonomy = %(here)s/taxonomy.xml
addo.render = %(here)s/my_template.html
addo.output = %(here)s/some_dir_somewhere
```

When using an ini style configuration you can override specific options by specifying them on the command line:

```bash
$ addo myconfig.ini -o some_other_location
```

Example
-------
There is an example set of data in the `example` directory, with an example configuration file. Provided Addo is
installed correctly in your path, running the example set of files is as easy as:

```bash
$ cd /where/ever/addo/is/example
$ addo config.ini
```

Or if you prefer to specify the command line options:

```bash
$ cd /where/ever/addo/is/example
$ addo -d destinations.xml -t taxonomy.xml -o output
```


Unit Tests
----------
Addo has 100% coverage by unit tests as reported by nose. Tests are contained in the tests directory and can be run
with nose, or distutils.

For example:

```bash
$ nosetests 
```

To get coverage you will need to install the coverage module:

```bash
$ pip install coverage
$ nosetests --with-coverage --cover-package=addo
```

Current Output:
```
Name                 Stmts   Miss  Cover   Missing
--------------------------------------------------
addo                     0      0   100%   
addo.destination        32      0   100%   
addo.legacy_parser     101      0   100%   
addo.render             14      0   100%   
addo.script             72      0   100%   
--------------------------------------------------
TOTAL                  219      0   100%   
----------------------------------------------------------------------
Ran 60 tests in 0.109s

OK
```

Future Enhancements
-------------------

 - The templating system should be extended to a little more generic, so that other templating systems could be used.
   (Such as Jinja, Chameleon, etc)
 - The Mako render should be extended so that it can be configured to use TemplateLookup from a directory, enabling
   inheritance, and all the other good features of Mako.


Why the name?
-------------
It is a latin word with the following meaning:

> To give, bring, place, / inspire, cause, / add, join

And is the root word for the english words **add** and **addendum**.

Reference: http://en.wiktionary.org/wiki/addo

