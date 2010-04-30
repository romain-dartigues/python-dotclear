from unittest import TestSuite, TextTestRunner

import test_re_html

test_suites = (
	test_re_html.suite(),
)

def suite():
	"Builds a test suite."
	s = TestSuite()
	map(s.addTest, test_suites)
	return s

def run(verbosity=1):
	"Runs the tests."
	TextTestRunner(verbosity=verbosity).run(suite())

if __name__ == '__main__':
	run(0)
