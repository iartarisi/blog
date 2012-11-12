#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
import codecs
import random

import config
from post import Post

class InitializationTestCase(unittest.TestCase):
    def setUp(self):
        self.post = config.datadir + '08-01-01-10:00-foo-bar'
        f = codecs.open(self.post, 'w')
        f.write('name\n---\n\nh1. foo bar baz bâș\n')  # it's unicode!
        f.close()
        self.p = Post(self.post)
    
    def tearDown(self):
        os.remove(self.post)

    def test_date(self):
        self.assertEqual(self.p.year, 2008, "can't read year from filename")
        self.assertEqual(self.p.month, 01, "can't read month from filename")
        self.assertEqual(self.p.day, 1, "can't read day from filename")

        self.assertEqual(self.p.month_name, 'January', 'wrong monthname')
        self.assertEqual(self.p.pretty_date, 'Tuesday, January  1, 2008', 
            'prettydate fails')
    
    def test_url(self):
        self.assertEqual(self.p.slug, 'foo-bar', "slug isn't parsed correctly")
        self.assertEqual(self.p.url, config.link + 'perma/foo-bar', "url incorrect!\n" + self.p.url)
    
    def test_name(self):
        self.assertEqual(self.p.name, 'name', "name incorrectly parsed!")
    
    def test_unicode(self):
        self.assertRaises(ValueError, Post, self.post, encoding='ascii')
   
    def test_body(self):
        self.assertEqual(self.p.body, 
                         ' <h1>foo bar baz b\xc3\xa2\xc8\x99</h1>',
                         'processing fails!' + self.p.body)

class ProcessingTestCase(InitializationTestCase):
    def test_markup(self):
        self.assertEqual(self.p.markup('h1. pyblee'), "\t<h1>pyblee</h1>", 
                'markup fails!' + self.p.markup('h1. pyblee'))
    
    def test_highlight(self):
        self.assertEqual(self.p.highlight(
                         '<pre lang="python">import this</pre>'),
                         '<div class="Python"><div class="highlight"><pre><span class="kn">import</span> <span class="nn">this</span>\n</pre></div>\n</div>', 
                         "pygments highlight fails!")


if __name__ == "__main__":
    unittest.main()
