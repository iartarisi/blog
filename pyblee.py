import sys
import os

import datetime
from textile import textile
from mako.template import Template
from mako.lookup import TemplateLookup

from config import *

temp_lookup = TemplateLookup(directories=[templatedir])

class Post:
    def __init__(self, file):
        """Initializes a Post object with these fields: date, slug, entry"""
        (dir, self.filename) = os.path.split(file)
        #self.date = datetime.datetime(int(self.filename[:2]), 
        #        int(self.filename[3:5]), int(self.filename[6:8])) # yy-mm-dd
        self.slug = self.filename[9:]
        self.url = sitedir + self.slug 
        f = open(datadir+self.filename, 'r')
        self.entry = textile(f.read())
        f.close()

    def write(self):    
        db_entry = open( sitedir + self.slug, 'w')
        db_entry.write( self.process(self.entry) )
        db_entry.close()

    def process(self, entry):
        """Returns the final html, ready to be rendered"""
        templ = temp_lookup.get_template('post.html')
        return templ.render(
                #entry = [textile(entry)], 
                title = title +' | '+ self.slug,
                posts = [self]
                )

class Blog:
    def __init__(self):
        self.title = title
        self.author = author
        self.email = email
    
    def get_index(self, posts_no):
        """Get entries from database and return a list of them"""
        files = os.listdir(datadir)
        files.sort()
        index = []
        for file in files[:posts_no]:
            post = Post(file)
            post.entry = textile(post.entry)
            index.append(post)
        return index

    def templatize(self, posts):
        templ = temp_lookup.get_template('post.html')
        return templ.render(
                posts = posts,
                title = title)

    def write(self, posts_no):
        """Write everything to a file"""
        f = open(sitedir+'index.html','w')
        f.write(self.templatize(self.get_index(posts_no)))
        f.close()

    def layout(self):
        """Get the list of posts through the template"""
        templ = Template(filename="index.html")
        return 

    def push(self, post):
        """Push new post to the database"""
        pass

    def update_post(self, post):
        """Update post (it already exists)"""
        pass

    def paginate(self):
        pass

if __name__ == '__main__':
    if len(sys.argv) == 3 or 2:
        if sys.argv[1] == 'post':
            post = Post(sys.argv[2])
            post.write()
        elif  sys.argv[1] == 'index':
            blog = Blog()
            blog.write(5)
    else:
        print 'you suck!' # help?
