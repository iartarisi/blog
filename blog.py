import os

from mako.lookup import TemplateLookup

from config import title, author, email, sitedir, datadir, posts_no, templatedir
from post import Post

class Blog:
    def __init__(self):
        self.title = title
        self.author = author
        self.email = email
        self.temp_lookup = TemplateLookup(directories=[templatedir], default_filters=['decode.utf8'])
    
    def get_index(self, posts_no=0):
        """Get posts from database and return a list of them (+textilize)"""
        files = os.listdir(datadir)
        files.sort(reverse=True)
        index = []
        if posts_no != 0:
            files = files[:7]
        for file in files:
            post = Post(file)
            index.append(post)
        return index

    def templatize(self, posts):
        templ = self.temp_lookup.get_template('post.html')
        return templ.render_unicode(
                posts = posts,
                title = title)

    def index(self):
        """Build the index page"""
        f = open(sitedir+'index.html','w')
        f.write(self.templatize(self.get_index(posts_no)).encode('utf-8'))
        f.close()
    
    def archive(self):
        """Build an archive page of all the posts, by date"""
        posts = self.get_index(0)
        
        #year = {} # dictionary of month names : lists of posts
        #mon = posts[0].month_name
        #months[mon] = [posts[0]]
        #years = {}
        #year = posts[0].year
        #years[year] = [months[0]]
        #for post in posts[1:]:
        #    if year != post.year:

        #    if mon != post.month_name:
        #        mon = post.month_name
        #        months[mon] = [post]
        #    else:
        #        months[mon].append(post)

        templ = self.temp_lookup.get_template('archive.html')
        processed_entry = templ.render(posts = posts, title = title)
        
        f = open(sitedir+'archive.html','w')
        f.write(processed_entry)
        f.close()

    def update(self):
        """Update the entire site (after a change to the posts)"""
        self.index()
        self.archive()

    def update_all(self):
        """Update the entire site, also processing the posts"""
        files = os.listdir(datadir)
        for file in files:
            post = Post(file)
            post.write()
        self.update()
