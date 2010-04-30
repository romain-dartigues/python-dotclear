__serial__    = 2010, 4,30
__author__    = 'Romain Dartigues <romain.dartigues@gmail.com>'
__docformat__ = 'restructuredtext'
__all__ = (
	'Translator',
	'p_block',
	'p_inline',
)





import sre_compile
import sys





RULES_FLAGS = sre_compile.SRE_FLAG_MULTILINE | sre_compile.SRE_FLAG_VERBOSE | sre_compile.SRE_FLAG_UNICODE

RULES_BLOCK = (
	#? xmp and macro-block raw-html
	r'(?:^\s*///\s*(?P<macro>html)?\s*(?(macro)(?P<special>(?:(?!///$)(?:.|\n))*)|(?P<xmp>(?:(?!///$)(?:.|\n))*))(?:///))',
	#? pre
	r'(?P<pre> (?:(?<=\n\n)|^)   (?:^[ ].+(\n|$))+ )',
	#? list, ordered and unordered Matches them whole, separate items are parsed later. The list *must* start with a single bullet.
	r'(?P<list>^[ \t]*([*][^*\#]|[\#][^\#*]).*$(\n[ \t]*[*\#]+.*$)*)',
	#? head
	r'^\s*(?P<head>(?P<head_level>!{1,4})(?P<head_value>.*?))\s*$',
	#? hr separator
	r'(?P<hr>^\s*----\s*$)',
	#? citation
	r'^(?P<blockquote>>(.*) ([\#]!(\s+.*)?$)?(.|\n)+?)(?:^[^>]|^$)',
	#? paragraph
	r'(?:(?<=(\n\n)(?![/*#!]|----))|^) (?P<p> ^(?:(?:.+\n(?!\n))*(?:.+$)) \n?)',
	#? empty line
	r'(?P<nl>^\s*$ )',
)

p_block = sre_compile.compile('|'.join(RULES_BLOCK), RULES_FLAGS)

RULES_INLINE = (
	#? URLs (starting with an url scheme like HTTP)
	#TODO: r'(?P<url>(^|(?<=\s|[.,:;!?()/=]))(?P<escaped_url>~)?(?P<url_target> (?P<url_proto>https?|ftps?|ircs?|nntp|news|mailto|telnet|file):\S+?)($|(?=\s|[,.:;!?()](\s|$))))',
	r'(?P<uri>[a-zA-Z]+:/{,3}[%s]+/?[%s]*|%s)' %(
		r'A-Za-z0-9\-\.',
		r'\%\;\/\?\:\@\&\=\+\$\,\[\]A-Za-z0-9\-_\.\!\~\*\'\(\)\w#',
		r'\%\;\/\?\:\@\&\=\+\$\,\[\]A-Za-z0-9\-_\.\!\~\*\'\(\)'
	),
	#? image
	r'(?P<img>\050\050 (?P<img_src>%(word)s) (?: \| (?P<img_alt>%(word)s) (?: \| (?P<img_align>%(word)s) (?: \| (?P<img_desc>%(word)s))?)?)?  \051\051)' % {'word': r'(?: (?<![^\\](?=\|)) .)+'},
	#? escaped character
	r'(?P<escape>[\\] (?P<escaped_char>\S) )',
	#? emphasis
	r"(?:'' (?P<em>.+) (?<![\\])'')",
	#? stronger emphasis
	r'(?:__ (?P<strong>.+) (?<!\\)__)',
	#? line break
	r'(?P<br>%%%)',
	#? anchor
	r'(?:~\s*(?P<anchor>.+?)\s* (?<!\\)~)',
	#? link (a href)
	r'(?P<a>\[ (?: (?P<a_value>%(word)s) (?<!\\)\| )?  (?P<a_href>%(word)s) (?: \| (?P<a_lang>%(word)s) (?: \| (?P<a_title>%(word)s))?)? \])' % {'word': r'(?: (?<![^\\](?=\|)) .)+'},
	#? acronym
	r'(?:\?\?\s*? (?P<acronym>(?P<acronym_value>.+?) \s*? (?:\|\s*?(?P<acronym_title>.+)\s*?|\|)?) \s*?(?<![\\])\?\?)',
	#? citation
	r'(?P<cite>{{ (?P<cite_value>%(word)s) (?: \| (?P<cite_lang>%(word)s) (?: \| (?P<cite_cite>%(word)s) )?)?  }})' % {'word': r'(?: (?<![^\\](?=\|)) .)+'},
	#? monospace / code
	r'(?: @@ (?P<code>.+?) (?<![\\]) @@ )',
	#? insert
	r'(?: \+\+ (?P<ins>.+?) (?<![\\]) \+\+ )',
	#? delete
	r'(?: -- (?P<del>.+) (?<![\\]) -- )',
	#? foot note
	r'(?: (?<!\s|\\)\$\$(?P<footnote>  (?: (?<![^\\](?=\$\$)) .)+  ) \$\$)',
)

p_inline = sre_compile.compile(r'(?<!\\)(?:%s)' % ('|'.join(RULES_INLINE),), RULES_FLAGS)





class Translator(object):
	'''DotClear wiki2xhtml markup parser abstract superclass implementation
	
	This is a base class for translators whose methods should implement
	blocks and inlines tags.

	Unimplemented methods will call :meth:`Translator.warn` and return the
	input untouched.
	'''
	def run(self, data):
		'''Run the parser on data and return the result'''
		return p_block.sub(self.blocks, data)

	def blocks(self, match):
		'''Parse blocks, probably inlines and return the result'''
		try:
			return getattr(self, 'b_%s' % match.lastgroup)(match)
		except AttributeError, err:
			self.warn(match, 'missing block handler')
		return match.group()

	def inlines(self, match):
		'''Parse inlines, and return the result
		
		Call :meth:`self.warn` and return the untouched input if the the tag is not hooked in the subclass'''
		try:
			return getattr(self, 'i_%s' % match.lastgroup)(match)
		except AttributeError, err:
			self.warn(match, 'missing inline handler; %r' % (err,))
		return match.group()

	def warn(self, match, message):
		if __debug__:
			sys.stderr.write('warning: [%s](%d, %d): %s\n' % (match.lastgroup, match.start(), match.end(), message))
