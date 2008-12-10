#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
import codecs

from post import Post
from config import DATADIR, ENCODING

FILE = '08-01-01-foo-bar'
CONTENT = 'name\n---\n\nh1. foo bar baz bâș\n'.decode(ENCODING)

class InitializationTestCase(unittest.TestCase):
    def setUp(self):
        f = codecs.open(DATADIR+FILE, 'w')
        f.write(CONTENT.encode(ENCODING))
        f.close()
        self.p = Post(FILE)

    def tearDown(self):
        os.remove(DATADIR+FILE)

    def testDate(self):
        self.assertEqual(self.p.year, 2008, "can't read year from the filename")
        self.assertEqual(self.p.month, 01, "can't read month from filename")
        self.assertEqual(self.p.day, 01, "cant'read day from filename")

        self.assertEqual(self.p.month_name, 'January', 'wrong monthname')
        self.assertEqual(self.p.pretty_date, '1 January 2008', 
                'prettydate fails')
    def testUrl(self):
        self.assertEqual(self.p.slug, 'foo-bar', "slug isn't parsed correctly")
        self.assertEqual(self.p.url, 'foo-bar.html', "url incorrect!")
    def testName(self):
        self.assertEqual(self.p.name, 'name', "name incorrectly parsed!")
    def testUnicode(self):
        self.assertRaises(ValueError, Post, FILE, encoding='ascii')
    def testEntry(self):
        self.assertEqual(self.p.entry, 
                '<h1>foo bar baz b\xc3\xa2\xc8\x99</h1>', 'processing fails!')

class MarkUpHighlightTestCase(InitializationTestCase):
    def testMarkup(self):
        self.assertEqual(self.p.markup('h1. pyblee'), "<h1>pyblee</h1>", 
                'markup fails!')
    def testHighlight(self):
        self.assertEqual(self.p.highlight('<pre lang="python">import this</pre>'),
                '<div class="Python"><div class="highlight"><pre><span class="kn">import</span> <span class="nn">this</span>\n</pre></div>\n</div>', 
                "pygments highlight fails!")

        



if __name__ == "__main__":
    unittest.main()
