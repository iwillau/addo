import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()

requires = [
    'setuptools',
    'mako',
    'lxml',
]

setup(
    name='Addo',
    version='0.2',
    url='https://github.com/iwillau/addo',
    license='MIT',
    author='Will Wheatley',
    author_email='will@iwill.id.au',
    description='HTML Renderer of destination metadata',
    long_description=README,
    packages=find_packages(),
    install_requires=requires,
    zip_safe=False,
    package_data={'addo': ['*html']},
    test_suite='addo',
    entry_points="""\
    [console_scripts]
    addo = addo.script:main
    """,
)
