import os

from mako.lookup import TemplateLookup

import config
from post import Post

class Blog:
    def __init__(self, datadir=config.datadir, sitedir=config.sitedir):
        
        # get_index() should be self.posts ???

        # need to do something about the utf8 constant
        self.temp_lookup = TemplateLookup(directories=[config.templatedir], 
                                          default_filters=['decode.utf8'])
    
    def get_index(self, posts_no=None):
        """Get posts from database and return a list of them"""
        files = os.listdir(config.datadir)
        files.sort(reverse=True)
        posts = []
        if posts_no:
            files = files[:posts_no]
        
        for file in files:
            post = Post(file)
            posts.append(post)

        return posts

    def templatize(self, template, posts_no=None):
        """Runs the posts through the given template"""
        templ = self.temp_lookup.get_template(template)
            
        posts = self.get_index(posts_no)
        return templ.render_unicode(posts = posts).encode(config.encoding)

    def build_page(self, template, output_page, posts=None):
        """Build a blog page, using :template:"""
        rendered_template = self.templatize(template, posts)
        self.write(output_page, rendered_template)
        
    def write(self, file, rendered_temp):
        """Write the template to the specified file
            
           Arguments:
           :file: a file to be written to in the config.sitedir 
           :rendered_temp: string (#FIXME#: should it be utf-ed?) 
           returns nothing
        """
        f = open(config.sitedir+file, 'w')
        f.write(rendered_temp)
        f.close()

    def rss(self):
        """Generate the rss feed for the site"""


    def index(self):
        """Build the index page"""
        self.build_page('post.html', 'index.html', config.posts_no)     
    
    def archive(self):
        """Build an archive page of all the posts, by date"""
        self.build_page('archive.html', 'archive.html') 

    def update(self):
        """Update the entire site (after a change to the posts)"""
        self.index()
        self.archive()

    def update_all(self):
        """Update the entire site, also processing the posts"""
        files = os.listdir(config.datadir)
        for file in files:
            post = Post(file)
            post.write()
        self.update()
