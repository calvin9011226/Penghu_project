#!c:\users\user\desktop\研究所\計畫\澎湖\澎湖專案\ph_project_v1\venv38\scripts\python.exe

# $Id: rst2latex.py 5905 2009-04-16 12:04:49Z milde $
# Author: David Goodger <goodger@python.org>
# Copyright: This module has been placed in the public domain.

"""
A minimal front end to the Docutils Publisher, producing LaTeX.
"""

try:
    import locale
    locale.setlocale(locale.LC_ALL, '')
except:
    pass

from docutils.core import publish_cmdline

description = ('Generates LaTeX documents from standalone reStructuredText '
               'sources. '
               'Reads from <source> (default is stdin) and writes to '
               '<destination> (default is stdout).  See '
               '<http://docutils.sourceforge.net/docs/user/latex.html> for '
               'the full reference.')

publish_cmdline(writer_name='latex', description=description)
