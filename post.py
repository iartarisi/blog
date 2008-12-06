import os
import calendar

from mako.template import Template
from mako.lookup import TemplateLookup
from textile import textile

from config import sitedir, datadir, templatedir, title

class Post:
    def __init__(self, file):
        """Initializes a Post object with these fields: date, slug, entry"""
        (dir, self.filename) = os.path.split(file)
        
        self.month = int(self.filename[3:5])
        self.month_name = calendar.month_name[self.month]
        self.day = int(self.filename[6:8])

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
        
        self.entry = textile(self.entry)
        self.temp_lookup = TemplateLookup(directories=[templatedir])

    def write(self):    
        """Output the processed post"""

        db_entry = open(sitedir+self.slug+'.html', 'w')
        db_entry.write( self.template(self.entry) )
        db_entry.close()

    def template(self, entry):
        """Returns the final html, ready to be rendered"""
        
        templ = self.temp_lookup.get_template('post.html')
        return templ.render(
                #entry = [textile(entry)], 
                title = title +' | '+ self.slug,
                posts = [self]
                )
