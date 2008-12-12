#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
import codecs
from mako.template import Template

import config
from blog import Blog
from post import Post

class InitializationTestCase(unittest.TestCase):
    def setUp(self):
        self.datadir = 'testdata/'
        self.sitedir = 'testsite/'
        os.mkdir(self.datadir)
        os.mkdir(self.sitedir)

        f = codecs.open(self.datadir + '01-01-01-post', 'w', config.encoding)
        f.write('name\n---\n\nh1. foo bar baz bâș\n'.decode(config.encoding))
        f.close()
        self.post = Post(self.datadir+'01-01-01-post', sitedir=self.sitedir)
        self.post.write()
        self.blog = Blog(self.datadir, self.sitedir)
        self.template = Template("TEST: ${posts[0].body}", 
                            default_filters=['decode.utf8'])
    
    def tearDown(self):
        os.remove(self.datadir+'01-01-01-post')
        os.remove(self.sitedir+'post.html')
        os.rmdir(self.datadir)
        os.rmdir(self.sitedir)

    def testBaseTemplate(self):
        links = '<h3>Recent</h3>\n<ul><li><a href='+self.post.url+'>'+ \
                self.post.name+'</a></li></ul>'
        self.assertEqual(links, self.blog.base_template(), 
                         'base template fails!\n'+links+'\n'+self.blog.base_template())


if __name__ == "__main__":
    unittest.main()
