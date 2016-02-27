# -*- coding: utf-8 -*-
# Copyright (c) 2012-2016 Ionuț Arțăriși <ionut@artarisi.eu>
# This file is part of pyblee.

# pyblee is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# pyblee is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with pyblee.  If not, see <http://www.gnu.org/licenses/>.

import unittest
import os
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
        f = open(self.datadir + '01-01-01-10:00-post', 'w',
                 encoding=config.encoding)
        f.write('name\n---\n\nh1. foo bar baz bâș\n')
        f.close()
        self.post = Post(
            self.datadir+'01-01-01-10:00-post', sitedir=self.sitedir)
        self.post.write([self.post], [])
        self.blog = Blog(self.datadir, self.sitedir)
        self.template = Template(
            "TEST: ${posts[0].body}", default_filters=['decode.utf8'])

    def tearDown(self):
        os.remove(self.datadir+'01-01-01-10:00-post')
        os.remove(self.sitedir+config.postdir+'post.html')
        os.rmdir(self.sitedir+config.postdir)
        os.rmdir(self.datadir)
        os.rmdir(self.sitedir)
