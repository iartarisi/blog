import os

from textile import textile
from mako.lookup import TemplateLookup

from config import title, author, email, sitedir, datadir, posts_no, templatedir
from post import Post

class Blog:
    def __init__(self):
        self.title = title
        self.author = author
        self.email = email
        self.temp_lookup = TemplateLookup(directories=[templatedir])
    
    def get_index(self, posts_no=0):
        """Get entries from database and return a list of them (+textilize)"""
        files = os.listdir(datadir)
        files.sort(reverse=True)
        index = []
        if posts_no != 0:
            files = files[:7]
        for file in files:
            post = Post(file)
            post.entry = textile(post.entry)
            index.append(post)
        return index

    def templatize(self, posts):
        templ = self.temp_lookup.get_template('post.html')
        return templ.render(
                posts = posts,
                title = title)

    def write(self, action):
        """Write everything to a file"""
        if action == 'index':
            f = open(sitedir+'index.html','w')
            f.write(self.templatize(self.get_index(posts_no)))
            f.close()
        elif action == 'archive':
            f = open(sitedir+'archive.html','w')
            f.write(self.archive())
            f.close()

    def archive(self):
        """Build an archive page of all the posts, by date"""
        posts = self.get_index(0) 
        # get the month number from the filename
        key = posts[0].month_name
        months = {} # dictionary of month names : lists of posts
        months[key] = [posts[0]]
        for post in posts[1:]:
            if key != post.month_name:
                key = post.month_name
                months[key] = [post]
            else:
                months[key].append(post)

        templ = self.temp_lookup.get_template('archive.html')
        return templ.render(
                months = months,
                title = title)

    def update(self):
        """Update the entire site (after a change to the posts)"""
        self.write('index')
        self.write('archive')

    def paginate(self):
        pass
