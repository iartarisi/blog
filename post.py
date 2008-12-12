import os
import calendar
import codecs
import re

from mako.lookup import TemplateLookup
from textile import textile
from pygments import formatters, lexers, highlight
from BeautifulSoup import BeautifulSoup

import config

class Post:
    def __init__(self, file, sitedir=config.sitedir, encoding=config.encoding):
        """Initializes a Post object with these fields: date, slug, body

           Arguments:
           :file: relative path to pyblee
           :encoding: string representation of encoding

        """
        self.sitedir = sitedir
        self.encoding = encoding
        (dir, self.filename) = os.path.split(file)
       
        if re.match('((\d{2}-){3})', self.filename): # post or page? 
            y, m, d, s = re.match('(\d{2})-(\d{2})-(\d{2})-(.*)',
                                    self.filename).groups()
            self.year, self.month, self.day, self.slug = (y, m, d, s)
            
            # lots of date formatting:
            self.year = int(self.year) + 2000
            self.month = int(self.month)
            self.day = int(self.day)
            self.month_name = calendar.month_name[self.month]
            self.pretty_date = str(self.day)+' '+self.month_name+ \
                               ' '+str(self.year)
        else:
            self.slug = self.filename
       
        self.url = self.slug + '.html'
        # read file
        f = codecs.open(file, 'r', encoding)
        try:
            postu = f.read()
        except UnicodeDecodeError:
           raise ValueError, 'your config.encoding is bogus'
        f.close()

        # get the post title and the body
        try:
            (self.name, self.body) = postu.split('\n---\n\n', 1)
        except ValueError:
            raise ValueError, 'check the formatting: '+file
        
        self.body = self.highlight(self.markup(self.body))
        self.temp_lookup = TemplateLookup(directories=[config.templatedir], 
                                          default_filters=['decode.utf8'])

    def markup(self, body):
        """Uses textile to return a formatted unicode string"""
        return textile(body.encode(self.encoding), encoding=self.encoding, 
                       output=self.encoding)

    def highlight(self, body):
        soup = BeautifulSoup(body)
        preblocks = soup.findAll('pre')
        for pre in preblocks:
            if pre.has_key('lang'):
                code = ''.join([str(item) for item in pre.contents])
                lexer = lexers.get_lexer_by_name(pre['lang'])
                formatter = formatters.HtmlFormatter()
                code_hl = highlight(code, lexer, formatter)
                pre.contents = [BeautifulSoup(code_hl)]
                pre.name = 'div'
                del(pre['lang'])
                pre['class'] = lexer.name
        return str(soup)

    def write(self):    
        """Output the processed post"""

        db_post = open(self.sitedir+self.slug+'.html', 'w')
        if self.filename == self.slug: # page
            db_post.write(self.template('page.html'))
        else:
            db_post.write(self.template('post.html'))
            print 'Post added: '+self.name +' -- '+self.pretty_date
        db_post.close()

    def template(self, temp='post.html'):
        """Returns the final html, ready to be rendered"""
        
        templ = self.temp_lookup.get_template(temp)
        return templ.render_unicode(posts = [self]).encode('utf-8')
