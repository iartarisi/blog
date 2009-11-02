import os
import re
import codecs
import cgi

from mako.lookup import TemplateLookup
from BeautifulSoup import BeautifulSoup
import config
from post import Post
from rss import Rss

class Blog:
    def __init__(self, datadir=config.datadir, sitedir=config.sitedir):
        """Get the posts into self.posts, and build the temp_lookup"""
       
        self.datadir = datadir
        self.sitedir = sitedir
        self.tags = {}
        # FIXME need to do something about the utf8 constant
        self.temp_lookup = TemplateLookup(directories=[config.templatedir], 
                                          default_filters=['decode.utf8'])
    
        # get posts from database and return a list of them
        files = os.listdir(datadir)
        files.sort(reverse=True)
        self.posts = []
        self.pages = []
        for f in files:
            if re.match('((\d{2}-){3})', f):
                post = Post(datadir+f)
                self.posts.append(post)
                if post.tags:
                    for tag in post.tags:
                        if tag not in self.tags.keys():
                            self.tags[tag] = [post]
                        else:
                            self.tags[tag].append(post)
            elif f[0] != '.': # not hidden -> page
                page = Post(datadir+f)
                self.pages.append(page)


    def templatize(self, template, posts, tag=None):
        """Runs the posts through the given template"""
        templ = self.temp_lookup.get_template(template)
            
        return templ.render_unicode(posts = posts, 
                                    tag = tag).encode(config.encoding)

    def build_page(self, template, output_file, posts, tag=None):
        """Build a blog page/post

           Build a blog page/post, using :template: and writing the file to disk
        """
        rendered_template = self.templatize(template, posts, tag)
        self.write(self.sitedir+output_file, rendered_template)
        
    def write(self, filename, rendered_temp):
        """Write the template to the specified file
            
           Arguments:
           :file: a file to be written to in the sitedir 
           :rendered_temp: string (FIXME: should it be utf-ed?) 
           
           returns nothing
        """
        f = open(filename, 'w')
        f.write(rendered_temp)
        f.close()
        print 'Wrote ' + filename + ' succesfully'

    def base_template(self, base_temp='base.html'):
        """Update the base template
        
           Update: recent posts, page links 
        """
        f = codecs.open(config.templatedir+base_temp, 'r', config.encoding)
        soup = BeautifulSoup(f.read())
        f.close()

        # update the recent posts
        recent = soup.find('div', id='recent')
        rec_html = '<div id="recent">\n<h4>Recent</h4>\n<ul>\n'
        for post in self.posts[:config.recent]:
            rec_html += '<li><a href="'+post.url+'">'+post.name+'</a></li>\n'
        rec_html += '</ul>\n</div>'
        recent.replaceWith(rec_html)

        # update the page links
        # FIXME ugly ugly view code should go in the view
        header = soup.find('div', id='header')
        h1_html = '<div id="header">\n' + str(header.h1)
        h1_html += '<a href="/">home</a>\n'
        h1_html += '<a href="/archive">archive</a>\n'
        for page in self.pages:
            if page.slug == page.filename: # FIXME better way to find pages?
                h1_html += '<a href="/'+page.slug+'">'+page.name+'</a>\n'
        h1_html += '\n</div>'
        header.replaceWith(h1_html)

        # update the tags
        tags = soup.find('div', id='tags')
        tag_html = '<div id="tags">\n<h4>Tags</h4>\n<ul>\n'
        for tag in self.tags:
            tag_html += '<li><a href="/'+config.tagdir+tag+'.html">'+tag \
                        +'</a></li>\n'
        tag_html += '</ul>\n</div>'
        tags.replaceWith(tag_html)

        self.write(config.templatedir+base_temp, str(soup))
        return (rec_html, h1_html, tag_html) 

    def build_rss(self, post_list):
        """Build an rss object and return a rendered rss template"""
        rss = Rss()
        temp = self.temp_lookup.get_template('rss.xml')
        
        return temp.render_unicode(posts = post_list, 
                                   rss = rss).encode(config.encoding)

    def rss(self):
        """Give the order to build all the rss pages"""
        # cleanup here, so it gets done once and only for rss
        # FIXME: this is tightly coupled b/c it changes the posts'
        for post in self.posts:
            post.body = cgi.escape(post.body)
       
        for tag in self.tags:
            self.write(self.sitedir+config.tagdir+tag+'.xml', 
                    self.build_rss(self.tags[tag]))
        self.write(self.sitedir+'feed.xml', 
                self.build_rss(self.posts[:config.posts_no]))

    def build_tags(self):
        """Build the pages relevant to each tag"""
        for tag in self.tags:
            self.build_page('post.html', config.tagdir+tag+'.html', 
                    self.tags[tag], tag=tag)

    def index(self):
        """Build the index page if it doesn't already exist"""
        self.build_page('post.html', 'index.html', 
                self.posts[:config.posts_no])     
    
    def archive(self):
        """Build an archive page of all the posts, by date"""
        self.build_page('archive.html', 'archive', self.posts) 
    
    def update_blog(self):
        """Update the entire site, also processing the posts"""
        self.base_template()
        self.update_site()
        self.index()
        self.archive()
        self.build_tags()
        self.rss()

    def update_site(self):
        """Updates only the static pages"""
        files = os.listdir(self.datadir)
        for f in files:
            if f[0] != '.': # leave out hidden files
                post = Post(self.datadir+f)
                post.write()
