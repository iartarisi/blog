import os
import calendar
import datetime
import codecs
import re
import pytz

from mako.lookup import TemplateLookup
from textile import textile
from pygments import formatters, lexers, highlight
from BeautifulSoup import BeautifulSoup

import config

class Post:
    def __init__(self, file, sitedir=config.sitedir, 
                 postdir=config.postdir, encoding=config.encoding):
        """Initializes a Post object with these fields: date, slug, body

           Arguments:
           :file: relative path to pyblee
           :encoding: string representation of encoding

        """
        self.sitedir = sitedir
        self.postdir = postdir
        self.encoding = encoding
        (dir, self.filename) = os.path.split(file)
       
        eurbuc = pytz.timezone('Europe/Bucharest')
        if re.match('((\d{2}-){3})', self.filename): # post or page? 
            y, m, d, H, M, self.slug = re.match('(\d{2})-(\d{2})-(\d{2})-(\d{2}):(\d{2})-(.*)',
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
        f = codecs.open(file, 'r', encoding)
        try:
            postu = f.read()
        except UnicodeDecodeError:
           raise ValueError, 'your config.encoding is bogus '+file
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
                raise ValueError, 'check formatting: '+ file
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

        if self.filename == self.slug: # page
            db_post = open(self.sitedir+self.slug, 'w')
            db_post.write(self.template('page.html'))
            print 'Page updated: '+self.name
        else:
            db_post = open(self.sitedir+self.postdir+self.slug, 'w')
            db_post.write(self.template('post.html'))
            # move posts in the directories specific to their tags
            print 'Post added: '+self.name +' -- '+self.pretty_date
        db_post.close()

    def template(self, temp='post.html'):
        """Returns the final html, ready to be rendered"""
        
        templ = self.temp_lookup.get_template(temp)
        return templ.render_unicode(posts = [self]).encode('utf-8')
