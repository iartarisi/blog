import os
import calendar

from mako.template import Template
from mako.lookup import TemplateLookup
from textile import textile
from BeautifulSoup import BeautifulSoup
from pygments import formatters, lexers, highlight

from config import sitedir, datadir, templatedir, title

class Post:
    def __init__(self, file, datetime=None):
        """Initializes a Post object with these fields: date, slug, entry"""
        (dir, self.filename) = os.path.split(file)
        
        self.year = '20'+self.filename[0:2]
        self.month = int(self.filename[3:5])
        self.month_name = calendar.month_name[self.month]
        self.day = self.filename[6:8]

        self.pretty_date = self.day+' '+self.month_name+' '+self.year

        self.slug = self.filename[9:]
        self.url = self.slug + '.html'
        f = open(datadir+self.filename, 'r')
        postu = f.read()
        f.close()
        
        # get the post title and the entry
        try:
            (self.title, self.entry) = postu.split('\n---\n\n', 1)
        except ValueError:
            raise ValueError, 'check the formatting: '+file

        self.entry =self.highlight(textile(self.entry))
        self.temp_lookup = TemplateLookup(directories=[templatedir])

    def highlight(self, entry):
        soup = BeautifulSoup(entry)
        preblocks = soup.findAll('pre')
        for pre in preblocks:
            if pre.has_key('lang'):
                code = ''.join([unicode(item) for item in pre.contents])
                lexer = lexers.get_lexer_by_name(pre['lang'])
                formatter = formatters.HtmlFormatter()
                code_hl = highlight(code, lexer, formatter)
                pre.contents = [BeautifulSoup(code_hl)]
                pre.name = 'div'
                del(pre['lang'])
                pre['class'] = lexer.name
        return unicode(soup)

    def write(self):    
        """Output the processed post"""

        db_entry = open(sitedir+self.slug+'.html', 'w')
        db_entry.write( self.template(self.entry) )
        db_entry.close()

    def template(self, entry):
        """Returns the final html, ready to be rendered"""
        
        templ = self.temp_lookup.get_template('post.html')
        return templ.render(
                title = title +' | '+ self.slug,
                posts = [self]
                )
