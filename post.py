import os
import calendar
import codecs

from mako.template import Template
from mako.lookup import TemplateLookup
from textile import textile
import BeautifulSoup
from pygments import formatters, lexers, highlight

from config import sitedir, datadir, templatedir, title

class Post:
    def __init__(self, file, datetime=None):
        """Initializes a Post object with these fields: date, slug, entry"""
        (dir, self.filename) = os.path.split(file)
        
        self.year = int('20'+self.filename[0:2])
        self.month = int(self.filename[3:5])
        self.month_name = calendar.month_name[self.month]
        self.day = int(self.filename[6:8])

        self.pretty_date = str(self.day)+' '+self.month_name+' '+str(self.year)

        self.slug = self.filename[9:]
        self.url = self.slug + '.html'
        f = codecs.open(datadir+self.filename, 'r', 'utf-8')
        postu = f.read()
        f.close()
        
        # get the post title and the entry
        try:
            (self.title, self.entry) = postu.split('\n---\n\n', 1)
        except ValueError:
            raise ValueError, 'check the formatting: '+file

        self.entry = self.highlight(textile(self.entry.encode('utf-8')))
        self.temp_lookup = TemplateLookup(directories=[templatedir], default_filters=['decode.utf8'])

    def highlight(self, entry):
        soup = BeautifulSoup.BeautifulSoup(entry)
        preblocks = soup.findAll('pre')
        for pre in preblocks:
            if pre.has_key('lang'):
                code = ''.join([str(item) for item in pre.contents])
                lexer = lexers.get_lexer_by_name(pre['lang'])
                formatter = formatters.HtmlFormatter()
                code_hl = highlight(code, lexer, formatter)
                pre.contents = [BeautifulSoup.BeautifulSoup(code_hl)]
                pre.name = 'div'
                del(pre['lang'])
                pre['class'] = lexer.name
        return str(soup)

    def write(self):    
        """Output the processed post"""

        db_entry = open(sitedir+self.slug+'.html', 'w')
        db_entry.write( self.template().encode('utf-8') )
        db_entry.close()

    def template(self):
        """Returns the final html, ready to be rendered"""
        
        templ = self.temp_lookup.get_template('post.html')
        return templ.render_unicode(
                title = title +' | '+ self.slug,
                posts = [self]
                )
