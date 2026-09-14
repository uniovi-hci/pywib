import os
import sys
sys.path.insert(0, os.path.abspath('../../src'))
import pybtex.plugin
from pybtex.style.formatting.unsrt import Style as UnsrtStyle
from pybtex.style.template import (
    names, sentence, field, optional, words, 
)

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'pywib'
copyright = '2025, Guillermo Dylan Carvajal Aza, Alejandro Álvarez Varela'
author = 'Guillermo Dylan Carvajal Aza, Alejandro Álvarez Varela'
release = '1.1.2'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = []

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.mathjax",
    "sphinx_autodoc_typehints",
    "sphinxcontrib.bibtex",
    "myst_parser",
]

# When True (default) Sphinx prefixes documented object names with the
# full module path. Set to False to show just the object name in
# autodoc/autosummary signatures 
add_module_names = False

# Bibliography for sphinxcontrib-bibtex
bibtex_bibfiles = ['references.bib']

class APAStyle(UnsrtStyle):
    def format_article(self, e):
        template = sentence [
            names('author', sep=', ', sep2=', ', last_sep=', '),  
            field('year', prefix='. (', suffix='). '),           
            field('title', suffix='. '),                          
            field('journal', suffix='. '),
            optional [ field('volume', prefix='Vol. ', suffix='. ') ],
            optional [ field('pages', prefix='pp. ', suffix='. ') ],
            optional [ field('url', prefix='', suffix='') ],
        ]
        return template.format_data(e)

    def format_incollection(self, e):
        template = sentence [
            names('author', sep=', ', sep2=', ', last_sep=', '),
            field('year', prefix='. (', suffix=').' ),
            field('title', suffix='. '),
            words [
                field('booktitle', prefix='In ', suffix=''),
                optional [ field('edition', prefix=' (', suffix=' ed.)') ],
                optional [ field('pages', prefix=', pp. ', suffix='') ],
                field('publisher', prefix='. ', suffix='.'),
            ],
            optional [ field('url', prefix=' ', suffix='') ],
        ]
        return template.format_data(e)

    def format_book(self, e):
        template = sentence [
            names('author', sep=', ', sep2=', ', last_sep=', '),
            field('year', prefix='. (', suffix='). '),
            field('title', suffix='. '),
            field('publisher', suffix='. '),
            optional [ field('edition', suffix=' ed. ') ],
            optional [ field('pages', prefix='pp. ', suffix='. ') ],
            optional [ field('url', prefix='', suffix='') ],
        ]
        return template.format_data(e)

    def format_labels(self, sorted_entries):
        for entry in sorted_entries:
            label = self.format_label(entry)
            yield [label]
    
pybtex.plugin.register_plugin('pybtex.style.formatting', 'apa', APAStyle)

# Use your new style for sphinxcontrib-bibtex
bibtex_default_style = 'apa'
bibtex_reference_style = 'author_year'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_favicon = 'favicon.ico'
html_static_path = ['_static']

def setup(app):
    app.add_css_file("custom.css")