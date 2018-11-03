#!/usr/bin/env python
# vim:ts=8 sw=8 ai noet encoding=utf-8
import os
import sys
import unittest

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


from dotclear import re_html





class TestWiki2XHTML(unittest.TestCase):
	def setUp(self):
		self.w2x = re_html.Wiki2XHTML()

	def _test(self, raw, html, skip_blocks=False):
		self.assertEqual(
			self.w2x.run(raw, skip_blocks=skip_blocks),
			html
		)



class TestSimpleBlocks(TestWiki2XHTML):
	def test_p(self):
		self._test(
			'Paragraphe 1.\n\nParagraphe 2.',
			'<p>Paragraphe 1.</p>\n\n<p>Paragraphe 2.</p>\n'
		)

	def test_headers(self):
		for raw, html in (
			('!!!Titre', '<h3>Titre</h3>\n'),
			('!!Titre', '<h4>Titre</h4>\n'),
			('!Titre', '<h5>Titre</h5>\n')
		):
			self._test(raw, html)

	def test_hr(self):
		self._test('----', '<hr />\n')

	def test_pre(self):
		self._test(
			u' Un espace au début\n de chaque ligne ',
			u'<pre>Un espace au d\xe9but\nde chaque ligne</pre>\n'
		)

	def test_xmp(self):
		self._test(
			u'///\nBloc de texte\npréformaté\nrespectant les espaces et les retours à la ligne.\n///',
			u'<pre class="xmp">Bloc de texte\npr\xe9format\xe9\nrespectant les espaces et les retours \xe0 la ligne.</pre>\n'
		)

	def test_blockquote(self):
		self._test(
			u'> Bloc de citation.\n>\n> Lorem ipsum...\n',
			u'<blockquote><p>Bloc de citation.</p>\n<p>Lorem ipsum...</p></blockquote>\n'
		)

	def test_ul(self):
		self._test(
			u'* premier item\n* deuxième item\n* troisième item',
			u'<ul>\n <li>premier item</li>\n <li>deuxi\xe8me item</li>\n <li>troisi\xe8me item</li>\n</ul>'
		)
	def test_ol(self):
		self._test(
			'# item 1\n# item 2\n# item 3',
			u'<ol>\n <li>item 1</li>\n <li>item 2</li>\n <li>item 3</li>\n</ol>'
		)

	def test_ulol(self):
		self._test(
			u'* premier item\n** premier sous-premier item\n** deuxième sous-premier item\n* deuxième item\n*# et on peut même mélanger\n*# ordonné et non ordonné\n* troisème item ',
			u'<ul>\n <li>premier item\n  <ul>\n   <li>premier sous-premier item</li>\n   <li>deuxi\xe8me sous-premier item</li>\n  </ul>\n </li>\n <li>deuxi\xe8me item\n  <ol>\n   <li>et on peut m\xeame m\xe9langer</li>\n   <li>ordonn\xe9 et non ordonn\xe9</li>\n  </ol>\n </li>\n <li>trois\xe8me item </li>\n</ul>'
		)



class TestSimpleInlines(TestWiki2XHTML):
	def _test(self, *args, **kwargs):
		super(self.__class__, self) \
			._test(*args, skip_blocks=True, **kwargs)

	def test_em(self):
		self._test("''emphase''", '<em>emphase</em>')

	def test_strong(self):
		self._test(
			'__forte emphase__',
			'<strong>forte emphase</strong>'
		)

	def test_ins(self):
		self._test('++insert++', '<ins>insert</ins>')

	def test_del(self):
		self._test('--suppression--', '<del>suppression</del>')

	def test_acronym(self):
		self._test(
			'??acronyme|titre??',
			u'<acronym title="titre">acronyme</acronym>'
		)

	def test_code(self):
		self._test('@@code@@', '<tt class="code">code</tt>')

	def test_br(self):
		self._test(
			u'Première ligne%%%\nDeuxième ligne',
			u'Première ligne<br />\nDeuxième ligne'
		)

	def test_a(self):
		for raw, html in (
			('[url]', '<a href="url">url</a>'),
			('[nom|url]', '<a href="url">nom</a>'),
			('[nom|url|langue]', '<a href="url" hreflang="langue">nom</a>'),
			('[nom|url|langue|titre]', '<a href="url" title="titre" hreflang="langue">nom</a>'),
		):
			self._test(raw, html)

	def test_url(self):
		url = 'http://www.example.net/?this=is+an%20automated#url'
		self._test(url, '<a href="%(url)s" class="external">%(url)s</a>' % locals())

	def test_img(self):
		for raw, html in (
			('((url))', u'<img src="url" />'),
			('((url|texte alternatif))', u'<img src="url" alt="texte alternatif" />'),
			('((url|texte alternatif|C))', u'<img src="url" alt="texte alternatif" style="display:block; margin:0 auto;" />'),
			('((url|texte alternatif|R|description longue))', u'<img src="url" alt="texte alternatif" longdesc="description longue" style="float:right; margin: 0 0 1em 1em;" />'),
		):
			self._test(raw, html)

	def test_anchor(self):
		self._test('~ancre~', '<a name="ancre"></a>')

	def test_cite(self):
		for raw, html in (
			('{{citation}}', '<q>citation</q>'),
			('{{citation|langue}}', '<q lang="langue">citation</q>'),
			('{{citation|langue|url source}}', '<q lang="langue" cite="url source">citation</q>'),
		):
			self._test(raw, html)

	def test_footnote(self):
		self._test(
			u'texte$$Corps de la note$$',
			u'texte<sup><a href="#wiki-footnote-1">1</a></sup>'\
			u'<div class="footnotes">\n <ol>\n  <li id="wiki-footnote-1">Corps de la note</li>\n </ol>\n</div>\n'
		)





def suite():
	s = unittest.TestSuite()
	s.addTest(unittest.makeSuite(TestSimpleBlocks))
	s.addTest(unittest.makeSuite(TestSimpleInlines))
	return s


def run(verbosity=2):
	unittest.TextTestRunner(verbosity=verbosity).run(suite())


if __name__ == '__main__':
	run()
