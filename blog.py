import os

from mako.lookup import TemplateLookup

from config import TITLE, AUTHOR, EMAIL, SITEDIR, DATADIR, POSTS_NO, TEMPLATEDIR
from post import Post

class Blog:
    def __init__(self):
        self.title = TITLE
        #self.link = LINK
        #self.description = DESCRIPTION
        self.author = AUTHOR
        self.email = EMAIL
        # get_index(0) should be self.posts - figure it out!
        self.temp_lookup = TemplateLookup(
                directories=[TEMPLATEDIR], default_filters=['decode.utf8'])
    
    def get_index(self, posts_no=0):
        """Get posts from database and return a list of them (+textilize)"""
        files = os.listdir(DATADIR)
        files.sort(reverse=True)
        index = []
        if posts_no != 0:
            files = files[:7]
        for file in files:
            post = Post(file)
            index.append(post)
        return index

    def templatize(self, template, posts_no=None):
        """Runs the posts through the given template"""
        templ = self.temp_lookup.get_template(template)
        if posts_no:
            posts = self.get_index(posts_no)
        else:
            posts = self.get_index(0)
        return templ.render_unicode(
                posts = posts,
                title = self.title).encode('utf-8')

    def index(self):
        """Build the index page"""
        
        rendered_temp = self.templatize('post.html', POSTS_NO)
        self.write('index.html', rendered_temp)
    
    def archive(self):
        """Build an archive page of all the posts, by date"""

        rendered_temp = self.templatize('archive.html')
        self.write('archive.html', rendered_temp)
        
    def write(self, file, rendered_temp):
        """Write the template to the specified file
            
           Arguments:
           :file: a file to be written to in the SITEDIR 
           :rendered_temp: string (#FIXME#: should it be utf-ed?) 
           returns nothing
        """
        f = open(SITEDIR+file, 'w')
        f.write(rendered_temp)
        f.close()

    def update(self):
        """Update the entire site (after a change to the posts)"""
        self.index()
        self.archive()

    def rss(self):
       """ """
       pass

    def update_all(self):
        """Update the entire site, also processing the posts"""
        files = os.listdir(DATADIR)
        for file in files:
            post = Post(file)
            post.write()
        self.update()
