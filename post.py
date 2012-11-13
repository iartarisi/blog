# -*- coding: utf-8 -*-
# Copyright (c) 2012 Ionuț Arțăriși <mapleoin@lavabit.com>
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

import datetime
import os
import re

from bs4 import BeautifulSoup, Tag
from textile import textile
from mako.lookup import TemplateLookup
from pygments import formatters, lexers, highlight

import config

class Post:
    def __init__(self, postfile, sitedir=config.sitedir, 
                 postdir=config.postdir, encoding=config.encoding):
        """Initializes a Post object with these fields: date, slug, body

           Arguments:
           :postfile: relative path to pyblee
           :encoding: string representation of encoding

        """
        self.sitedir = sitedir
        self.postdir = postdir
        self.encoding = encoding
        self.filename = os.path.split(postfile)[1]
       
        if re.match('((\d{2}-){3})', self.filename): # post or page? 
            y, m, d, H, M, self.slug = re.match(
                '(\d{2})-(\d{2})-(\d{2})-(\d{2}):(\d{2})-(.*)',
                self.filename).groups()
            date = datetime.datetime(int('20'+y),int(m),int(d), int(H), int(M))
            # lots of date formatting:
            (self.day, self.month, self.year)=(date.day, date.month, date.year)
            self.month_name = date.strftime('%B')
            self.pretty_date = date.strftime('%A, %B %e, %Y')
            self.pub_date = date.strftime("%a, %d %b %Y %H:%M GMT")
        else:
            self.slug = self.filename
       
        self.url = config.link + self.postdir + self.slug # + '.html'
        # read file
        f = open(postfile, 'r', encoding=encoding)
        try:
            postu = f.read()
        except UnicodeDecodeError:
            raise ValueError('Your config.encoding is bogus ' + postfile)
        f.close()

        # get the post title and the body
        try:
            splits = postu.split('\n---\n\n')
            if len(splits) == 3:
                self.name, self.tags, self.body = splits
                self.tags = self.tags.split(', ')
            elif len(splits) == 2:
                self.name, self.body = splits
                self.tags = None
            else:
                raise ValueError('Check formatting: '+ file)
        except ValueError:
            raise ValueError("Check the formatting (I'd like a title "
                             "and some tags, please!" + file)

        self.body = code_highlight(self.markup(self.body))
        self.temp_lookup = TemplateLookup(directories=[config.templatedir], 
                                          default_filters=['decode.utf8'])

    def markup(self, body):
        """Uses textile to return a formatted unicode string"""
        soup = BeautifulSoup(body)
        preblocks = soup.findAll('pre')
        # add a <notextile> tag inside every pre lang tag
        for pre in preblocks:
            if pre.has_key('lang'):
                notextile = soup.new_tag('notextile')
                notextile.insert(0, pre.contents[0])
                pre.clear()
                pre.insert(0, notextile)

        # textilize everything else
        return textile(repr(soup))

    def write(self, all_posts, all_tags):
        """Output the processed post"""
        if self.filename == self.slug: # page
            db_post = open(self.sitedir+self.slug+'.html', 'w',
                           encoding=config.encoding)
            db_post.write(self.template('page.html', all_posts, all_tags))
            print('Page updated: ' + self.name)
        else:
            db_post = open(self.sitedir+self.postdir+self.slug+'.html', 'w',
                           encoding=config.encoding)
            db_post.write(self.template('post.html', all_posts, all_tags))
            # move posts in the directories specific to their tags
            print('Post added: {0} -- {1}'.format(self.name, self.pretty_date))
        db_post.close()

    def template(self, temp, all_posts, all_tags):
        """Returns the final html, ready to be rendered"""
        
        templ = self.temp_lookup.get_template(temp)
        return templ.render_unicode(posts = [self],
                                    tag_page=False,
                                    config=config,
                                    all_posts=all_posts,
                                    all_tags=all_tags)


# the code in _highlight() and highlight() was adapted from the `mynt`
# project under a BSD license: Copyright (c) 2011, Andrew Fricke
def _code_highlight(match):
    language, code = match.groups()

    formatter = formatters.HtmlFormatter()
    # textile or mako in markup() likes to replace stuff with HTML
    # entities so we have to undo that for code blocks
    for pattern, replace in [
        ('&#34;', '"'), ('&#39;', '\''), ('&amp;', '&'), ('&apos;', '\''),
        ('&gt;', '>'), ('&lt;', '<'), ('&quot;', '"')]:
        code = code.replace(pattern, replace)

    lexer = lexers.get_lexer_by_name(language)

    code = highlight(code, lexer, formatter)

    return '<div class="{0}">{1}</div>'.format(lexer.name, code)

def code_highlight(body):
    """Syntax highlighting"""
    return re.sub(r'<pre[^>]+lang="([^>]+)"[^>]*>(.+?)</pre>',
                  _code_highlight, body, flags=re.S)
