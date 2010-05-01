#!/usr/bin/env python
# vim:ts=8 sw=8 ai noet encoding=utf-8
import os
import sys
import unittest

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


import re_parser





class TestBugs(unittest.TestCase):
	def test_inside_attribute_error(self):
		''':class:`Translator` must not hide subclasses errors
		'''
		class Buggy(re_parser.Translator):
			def i_del(self, match):
				return match.random_non_existing_attribute
			b_p = i_del
		self.assertRaises(AttributeError, Buggy().run, '--word--', skip_blocks=True)
		self.assertRaises(AttributeError, Buggy().run, 'word')




def suite():
	s = unittest.TestSuite()
	s.addTest(unittest.makeSuite(TestBugs))
	return s


def run(verbosity=3):
	unittest.TextTestRunner(verbosity=verbosity).run(suite())


if __name__ == '__main__':
	run(3)

