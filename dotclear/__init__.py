'''dotclear translator

Attempt to parse DotClear_ wiki2xhtml markup and provide hooks to translate it
into another format (i.e.: html, restructured text, ...).

.. Note::
   Currently support only the syntaxe-1.2_, syntaxe-2.0_ not supported yet.


.. _DotClear: http://www.dotclear.org/
.. _syntaxe-1.2: http://fr.dotclear.org/documentation/1.2/usage/syntaxes
.. _syntaxe-2.0: http://fr.dotclear.org/documentation/2.0/usage/syntaxes
'''
__version__ = '0.1'
__all__ = ['wiki2xhtml']





from dotclear import re_html





wiki2xhtml = re_html.Wiki2XHTML().run
