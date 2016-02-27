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

from collections import OrderedDict
import html
import os
import re

from bs4 import BeautifulSoup
from mako.lookup import TemplateLookup

import config
from post import Post
from rss import Rss

class Blog:
    def __init__(self, datadir=config.datadir, sitedir=config.sitedir):
        """Get the posts into self.posts, and build the temp_lookup"""
       
        self.datadir = datadir
        self.sitedir = sitedir
        self.tags = {}
        self.temp_lookup = TemplateLookup(directories=[config.templatedir])
    
        # get posts from database and return a list of them
        files = os.listdir(datadir)
        files.sort(reverse=True)
        self.posts = []
        self.pages = []
        for f in files:
            if re.match('((\d{2}-){3})', f):
                post = Post(datadir+f)
                self.posts.append(post)
                if post.tags:
                    for tag in post.tags:
                        if tag not in self.tags.keys():
                            self.tags[tag] = [post]
                        else:
                            self.tags[tag].append(post)
            elif f[0] != '.': # not hidden -> page
                page = Post(datadir+f)
                self.pages.append(page)

        # sort by tag name, ignoring capitalization
        self.tags = OrderedDict(
            sorted(self.tags.items(), key=lambda t: t[0].lower()))

    def templatize(self, template, posts, tag=None):
        """Runs the posts through the given template"""
        templ = self.temp_lookup.get_template(template)

        return templ.render(posts=posts,
                            all_posts=self.posts,
                            tag_page=tag,
                            all_tags=self.tags,
                            config=config,
                            encoding=config.encoding)

    def build_page(self, template, output_file, posts, tag=None):
        """Build a blog page/post

        Build a blog page/post, using :template: and writing the file to disk
        """
        rendered_template = self.templatize(template, posts, tag)
        self.write(self.sitedir+output_file, rendered_template)
        
    def write(self, filename, rendered_temp):
        """Write the template to the specified file
            
           Arguments:
           :file: a file to be written to in the sitedir 
           :rendered_temp: string (FIXME: should it be utf-ed?) 
           
           returns nothing
        """
        f = open(filename, 'w', encoding=config.encoding)
        f.write(rendered_temp)
        f.close()
        print('Wrote {0} succesfully'.format(filename))

    def build_rss(self, post_list):
        """Build an rss object and return a rendered rss template"""
        rss = Rss()
        temp = self.temp_lookup.get_template('rss.xml')
        
        return temp.render(posts = post_list, rss = rss)

    def rss(self):
        """Give the order to build all the rss pages"""
        # cleanup here, so it gets done once and only for rss
        # FIXME: this is tightly coupled b/c it changes the posts'
        for post in self.posts:
            post.body = html.escape(post.body, quote=False)
       
        for tag in self.tags:
            self.write(self.sitedir+config.tagdir+tag+'.xml', 
                    self.build_rss(self.tags[tag]))
        self.write(self.sitedir+'feed.xml', 
                self.build_rss(self.posts[:config.posts_no]))

    def build_tags(self):
        """Build the pages relevant to each tag"""
        for tag in self.tags:
            self.build_page('post.html', config.tagdir+tag+'.html', 
                    self.tags[tag], tag=tag)

    def index(self):
        """Build the index page if it doesn't already exist"""
        self.build_page('post.html', 'index.html', 
                self.posts[:config.posts_no])     
    
    def archive(self):
        """Build an archive page of all the posts, by date"""
        self.build_page('archive.html', 'archive.html', self.posts) 
    
    def update_blog(self):
        """Update the entire site, also processing the posts"""
        self.update_site()
        self.index()
        self.archive()
        self.build_tags()
        self.rss()

    def update_site(self):
        """Updates only the static pages"""
        files = os.listdir(self.datadir)
        for f in files:
            if f[0] != '.': # leave out hidden files
                post = Post(self.datadir+f)
                post.write(self.posts, self.tags)
