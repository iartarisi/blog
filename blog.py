import os
import re
import codecs

from mako.lookup import TemplateLookup
from BeautifulSoup import BeautifulSoup, Tag
import config
from post import Post

class Blog:
    def __init__(self, datadir=config.datadir, sitedir=config.sitedir):
        """Get the posts into self.posts, and build the temp_lookup"""
       
        self.datadir = datadir
        self.sitedir = sitedir
        # FIXME need to do something about the utf8 constant
        self.temp_lookup = TemplateLookup(directories=[config.templatedir], 
                                          default_filters=['decode.utf8'])
    
        # get posts from database and return a list of them
        files = os.listdir(datadir)
        files.sort(reverse=True)
        self.posts = []
        for file in files:
            if re.match('((\d{2}-){3})', file):
                post = Post(datadir+file)
                self.posts.append(post)


    def templatize(self, template, posts_no=None):
        """Runs the posts through the given template"""
        templ = self.temp_lookup.get_template(template)
            
        posts = self.posts[:posts_no]
        return templ.render_unicode(posts = posts).encode(config.encoding)

    def build_page(self, template, output_file, posts=None):
        """Build a blog page, using :template:"""
        rendered_template = self.templatize(template, posts)
        self.write(self.sitedir+output_file, rendered_template)
        
    def write(self, file, rendered_temp):
        """Write the template to the specified file
            
           Arguments:
           :file: a file to be written to in the sitedir 
           :rendered_temp: string (FIXME: should it be utf-ed?) 
           
           returns nothing
        """
        f = open(file, 'w')
        f.write(rendered_temp)
        f.close()
        print 'Wrote ' + file + ' succesfully'

    def base_template(self, base_temp='base.html'):
        """Update the base template adding the recent posts"""

        # This could turn into something like a widget at one time, but this
        # is faster since it's only done one time per update

        f = codecs.open(config.templatedir+base_temp, 'r', config.encoding)
        soup = BeautifulSoup(f.read())
        f.close()

        recent = soup.find('div',id='recent')

        string = '<div id="recent">\n<h3>Recent</h3>\n<ul>\n'
        for post in self.posts[:config.recent]:
            string += '<li><a href='+post.url+'>'+post.name+'</a></li>\n'
        string += '</ul>\n</div>'
        recent.replaceWith(string)

        self.write(config.templatedir+base_temp, str(soup))
        return string

    def index(self):
        """Build the index page"""
        self.build_page('post.html', 'index.html', config.posts_no)     
    
    def archive(self):
        """Build an archive page of all the posts, by date"""
        self.build_page('archive.html', 'archive.html') 

    def update_all(self):
        """Update the entire site, also processing the posts"""
        self.base_template()
        files = os.listdir(self.datadir)
        for file in files:
            post = Post(self.datadir+file)
            post.write()
        self.archive()
        self.index()
