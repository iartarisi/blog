import os
import calendar
import codecs

from mako.lookup import TemplateLookup
from textile import textile
from pygments import formatters, lexers, highlight
from BeautifulSoup import BeautifulSoup

import config

class Post:
    def __init__(self, file, encoding=config.encoding):
        """Initializes a Post object with these fields: date, slug, entry"""
        (dir, self.filename) = os.path.split(file)
        
        self.year = int('20'+self.filename[0:2])
        self.month = int(self.filename[3:5])
        self.month_name = calendar.month_name[self.month]
        self.day = int(self.filename[6:8])

        self.pretty_date = str(self.day)+' '+self.month_name+' '+str(self.year)

        self.slug = self.filename[9:]
        self.url = self.slug + '.html'
       
        # read file
        f = codecs.open(file, 'r', encoding)
        try:
            postu = f.read()
        except UnicodeDecodeError:
           raise ValueError, 'your config.encoding is bogus'
        f.close()

        # TODO maybe we could create/move the file to the datadir if it's not 
        # already there
        
        # get the post title and the entry
        try:
            (self.name, self.entry) = postu.split('\n---\n\n', 1)
        except ValueError:
            raise ValueError, 'check the formatting: '+file
        self.entry = self.highlight(self.markup(self.entry))
        self.temp_lookup = TemplateLookup(directories=[config.templatedir], 
                                          default_filters=['decode.utf8'])

    def markup(self, entry):
        """Uses textile to return a formatted unicode string"""
        return textile(entry.encode('utf-8'), encoding='utf-8', 
                       output='utf-8')

    def highlight(self, entry):
        soup = BeautifulSoup(entry)
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

        db_entry = open(config.sitedir+self.slug+'.html', 'w')
        db_entry.write( self.template() )
        db_entry.close()

    def template(self, temp='post.html'):
        """Returns the final html, ready to be rendered"""
        
        templ = self.temp_lookup.get_template(temp)
        return templ.render_unicode(posts = [self]).encode('utf-8')
