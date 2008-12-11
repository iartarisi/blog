import os

from mako.lookup import TemplateLookup

import config
from post import Post

class Blog:
    def __init__(self, datadir=config.datadir, sitedir=config.sitedir):
        """Get the posts into self.posts, and build the temp_lookup"""
        
        # get_index() should be self.posts ???

        # need to do something about the utf8 constant
        self.temp_lookup = TemplateLookup(directories=[config.templatedir], 
                                          default_filters=['decode.utf8'])
    
        # get posts from database and return a list of them
        files = os.listdir(config.datadir)
        files.sort(reverse=True)
        self.posts = []
        for file in files:
            post = Post(config.datadir+file)
            self.posts.append(post)


    def templatize(self, template, posts_no=None):
        """Runs the posts through the given template"""
        templ = self.temp_lookup.get_template(template)
            
        posts = self.posts[:posts_no]
        return templ.render_unicode(posts = posts).encode(config.encoding)

    def build_page(self, template, output_file, posts=None):
        """Build a blog page, using :template:"""
        rendered_template = self.templatize(template, posts)
        self.write(output_file, rendered_template)
        
    def write(self, file, rendered_temp):
        """Write the template to the specified file
            
           Arguments:
           :file: a file to be written to in the config.sitedir 
           :rendered_temp: string (FIXME: should it be utf-ed?) 
           
           returns nothing
        """
        f = open(config.sitedir+file, 'w')
        f.write(rendered_temp)
        f.close()

    def index(self):
        """Build the index page"""
        self.build_page('post.html', 'index.html', config.posts_no)     
    
    def archive(self):
        """Build an archive page of all the posts, by date"""
        self.build_page('archive.html', 'archive.html') 

    def update(self):
        """Update the entire site (after a change to on of the posts)"""
        self.index()
        self.archive()

    def update_all(self):
        """Update the entire site, also processing the posts"""
        files = os.listdir(config.datadir)
        for file in files:
            post = Post(config.datadir+file)
            post.write()
        self.update()
