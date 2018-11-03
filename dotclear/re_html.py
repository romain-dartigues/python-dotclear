r"""

Usage::
	>>> print re_html.Wiki2XHTML().run(u'''!''Dot''__Clear__ @@markup@@\n\nHello World.''')
	<h5><em>Dot</em><strong>Clear</strong> <tt class="code">markup</tt></h5>

	<p>Hello World.</p>

"""
__all__ = ['Wiki2XHTML']





import sre_compile
import itertools
import urlparse


from nodes import MazNode, LEAVE, EMPTY
from re_parser import Translator, p_inline





html_special_chars = {
	u"'": u'&apos;',
	u'"': u'&quot;',
	u'&': u'&amp;',
	u'<': u'&lt;',
	u'>': u'&gt;',
}
html_entities = dict((v.decode('latin1'), '&%s;'%k) for k, v in __import__('htmlentitydefs').entitydefs.iteritems() if len(v) == 1)



# FIXME: unescape chars before the output
# XXX: should we use :func:`urllib.quote` on href/src?
class Wiki2XHTML(Translator):
	'''Simple conversion from DotClear wiki2xhtml markup to HTML

	.. Warning::
	   Behaviour is quite different than the original DotClear parser and a
	   few elements has been left unimplemented.
	'''
	#? first space of each line
	_first_space = sre_compile.compile(r'(?:^|(?<=\n))(?:[ ]|(?=\n))')

	#? first '> ' sequence of each line, the space being optional
	_first_gt_space = sre_compile.compile(r'(?:^|(?<=\n))>(?:[ ]|(?=\n))')

	#? double or more LF
	_block_separator = sre_compile.compile(r'\n\n+(?=\S)')

	#? separate list prefix (# | *) and list value
	_fragment_list = sre_compile.compile(
		r'(?P<type>[*#]+) \s* (?P<value> (?: (?:(?:.|\n)+?) (?:(?=\n[#*])|$) ) | (?:.+\n)$ )',
		sre_compile.SRE_FLAG_MULTILINE|sre_compile.SRE_FLAG_VERBOSE
	)

	#? use to beautify ``<li>\n\s*value`` to ``<li>value``
	_li_trim = sre_compile.compile(r'(?<=<li>)\s+|(?<![>])(?=\n)\s+?(?=</li>)')

	#? non-word
	_non_word = sre_compile.compile(r'\W+')

	@staticmethod
	def escape(string, entities=False):
		'''Escape special HTML characters

		Replace characters with a special signifiance in HTML by their
		HTML entity equivalent.
		If the optional argument `entities` is set, will use an
		entities table build from :var:`htmlentitydefs.entitydefs`.
		'''
		tr = html_entities if entities else html_special_chars
		return u''.join(c in tr and tr[c] or c for c in string)

	##### blocks
	@staticmethod
	def b_hr(match):
		return u'<hr />\n'

	def b_p(self, match):
		return u'<p>%s</p>\n' % p_inline.sub(self.inlines, match.group('p')).strip()

	def b_xmp(self, match):
		return u'<pre class="xmp">%s</pre>\n' % self.escape(match.group('xmp')).strip()

	def b_pre(self, match):
		return u'<pre>%s</pre>\n' % p_inline.sub(
			self.inlines,
			self._first_space.sub('', match.group(match.lastgroup))
		).rstrip()

	def b_special(self, match):
		assert match.group('macro') == 'html'
		return u'<div class="macro %s">%s</div>\n' % (self.escape(match.group('macro')), match.group('special').strip())

	def b_head(self, match):
		return u'<h%(n)u>%(value)s</h%(n)u>\n' % {
			'n': 6-len(match.group('head_level')),
			'value': p_inline.sub(self.inlines, match.group('head_value'))
		}

	def b_blockquote(self, match):
		return u'<blockquote><p>%s</p></blockquote>\n' % u'</p>\n<p>'.join(
				self._block_separator.split(
					p_inline.sub(
						self.inlines,
						self._first_gt_space.sub(
							'',
							match.group(match.lastgroup)
						)
					)
				)
		).rstrip()

	def b_list(self, match):
		ltprev = ''
		#? TODO: i'd like to do it without the nodes tree
		root = node = MazNode('div')
		for m in self._fragment_list.finditer(match.group()):
			ltcurr, value = m.groups()
			for prev, curr in itertools.dropwhile(lambda x: not cmp(x[0], x[1]), itertools.izip_longest(ltprev, ltcurr)):
				if prev:
					node = node.parent
					if node.name == 'li':
						node = node.parent
				if curr:
					if node.child and node.child.name == 'li':
						node = node.child.prev
					node+= MazNode('%sl' %(curr == '#' and 'o' or 'u',))
					node = node.child.prev
			node+= (MazNode('li') + MazNode(value=p_inline.sub(self.inlines, value)))
			ltprev = ltcurr
		# FIXME: there is a bug in MazNode when descending from a higher level than the root
		root.child.parent = root.child
		return self._li_trim.sub('', node2html(root.child))

	@staticmethod
	def b_nl(match):
		return ''

	##### inlines
	def i_code(self, match):
		return u'<tt class="code">%s</tt>' % p_inline.sub(self.inlines, match.group(match.lastgroup))

	def i_em(self, match):
		return u'<em>%s</em>' % p_inline.sub(self.inlines, match.group(match.lastgroup))

	def i_strong(self, match):
		return u'<strong>%s</strong>' % p_inline.sub(self.inlines, match.group(match.lastgroup))

	def i_del(self, match):
		return u'<del>%s</del>' % p_inline.sub(self.inlines, match.group(match.lastgroup))

	def i_ins(self, match):
		return u'<ins>%s</ins>' % p_inline.sub(self.inlines, match.group(match.lastgroup))

	@staticmethod
	def i_br(match):
		return u'<br />'

	def i_anchor(self, match):
		return u'<a name="%s"></a>' % self._non_word.sub('-', match.group('anchor'))

	def i_acronym(self, match):
		return u'<acronym%s>%s</acronym>' % (
			u' title="%s"' % self.escape(match.group('acronym_title').strip()) if match.group('acronym_title') else '',
			p_inline.sub(self.inlines, match.group('acronym_value')).strip()
		)

	def i_a(self, match):
		href = urlparse.urlsplit(match.group('a_href'))
		link = [u'<a href="%s"' % match.group('a_href')]
		if match.group('a_title'):
			link.append(u' title="%s"' % self.escape(match.group('a_title')))
		if match.group('a_lang'):
			link.append(u' hreflang="%s"' % self.escape(match.group('a_lang')))
		if href.scheme:
			# TODO: make a handle for the external using the hostname
			link.append(u' class="external"')
		link.append(u'>%s</a>' % (
			p_inline.sub(self.inlines, match.group('a_value')) \
			if match.group('a_value') \
			else self.escape(match.group('a_href'))
		))
		return ''.join(link)

	def i_uri(self, match):
		return u'<a href="%s" class="external">%s</a>' % (
			match.group(match.lastgroup),
			self.escape(match.group(match.lastgroup))
		)

	def i_img(self, match):
		link = [u'<img src="%s"' % match.group('img_src')]
		if match.group('img_alt'):
			link.append(u'alt="%s"' % self.escape(match.group('img_alt')))
		if match.group('img_desc'):
			link.append(u'longdesc="%s"' % self.escape(match.group('img_desc')))
		if match.group('img_align'):
			align = match.group('img_align').strip().lower()[0]
			if align in 'lg':
				#? align left
				link.append('style="float:left; margin: 0 1em 1em 0;"')
			elif align in 'cm':
				#? align center
				link.append('style="display:block; margin:0 auto;"')
			elif align in 'rd':
				#? align right
				link.append('style="float:right; margin: 0 0 1em 1em;"')
			else:
				self.warn(match, 'unknown alignment %r' % match.group('img_align'))
		link.append('/>')
		return ' '.join(link)

	def i_cite(self, match):
		r = ['<q']
		if match.group('cite_lang'):
			r.append(u' lang="%s"' % self.escape(match.group('cite_lang')))
		if match.group('cite_cite'):
			# FIXME? use urlencode, not escape
			r.append(u' cite="%s"' % self.escape(match.group('cite_cite')))
		r.append(u'>%s</q>' % p_inline.sub(self.inlines, match.group('cite_value')).strip())
		return ''.join(r)


def node2html(node):
	'''Return a string representation of the node tree

	.. Warning::
	   This is a really specific minimalist implementation.
	'''
	data = []
	RS = u' '
	for status, node, depth in node.descend(node):
		if status == EMPTY:
			assert not node.name
			data.append(u'%s%s' % (RS*depth, node['value']) )
		else:
			data.append(u'%s<%s%s>' % (RS*depth, u'/' if status == LEAVE else u'', node.name))
	return u'\n'.join(data)
