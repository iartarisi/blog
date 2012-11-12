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
        os.mkdir(self.sitedir+config.postdir)
        f = codecs.open(self.datadir + '01-01-01-10:00-post', 'w', config.encoding)
        f.write('name\n---\n\nh1. foo bar baz bâș\n'.decode(config.encoding))
        f.close()
        self.post = Post(self.datadir+'01-01-01-10:00-post', sitedir=self.sitedir)
        self.post.write()
        self.blog = Blog(self.datadir, self.sitedir)
        self.template = Template("TEST: ${posts[0].body}", 
                            default_filters=['decode.utf8'])
    
    def tearDown(self):
        os.remove(self.datadir+'01-01-01-10:00-post')
        os.remove(self.sitedir+config.postdir+'post')
        os.rmdir(self.sitedir+config.postdir)
        os.rmdir(self.datadir)
        os.rmdir(self.sitedir)

    def test_base_template(self):
        links = '<div id="recent">\n<h4>Recent</h4>\n<ul>\n<li><a href="'+ \
                self.post.url+'">'+ self.post.name+'</a></li>\n</ul>\n</div>'
        self.assertEqual(links, self.blog.base_template(), 
                         'base template fails!\n'+links+'\n'+self.blog.base_template())
