#!c:\users\user\desktop\研究所\計畫\澎湖\澎湖專案\ph_project_v1\venv38\scripts\python.exe

# $Id: rstpep2html.py 4564 2006-05-21 20:44:42Z wiemann $
# Author: David Goodger <goodger@python.org>
# Copyright: This module has been placed in the public domain.

"""
A minimal front end to the Docutils Publisher, producing HTML from PEP
(Python Enhancement Proposal) documents.
"""

try:
    import locale
    locale.setlocale(locale.LC_ALL, '')
except:
    pass

from docutils.core import publish_cmdline, default_description


description = ('Generates (X)HTML from reStructuredText-format PEP files.  '
               + default_description)

publish_cmdline(reader_name='pep', writer_name='pep_html',
                description=description)
