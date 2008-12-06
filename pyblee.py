import sys
import os
from datetime import datetime

from blog import Blog
from post import Post

blog = Blog()
if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == 'post':
        post = Post(sys.argv[2])
        post.write()
        blog.update()
    elif len(sys.argv) == 2:
        if sys.argv[1] == 'index':
            blog.update()
        elif sys.argv[1] == 'archive':
            blog.archive()
        elif (sys.argv[1] == 'update'):
            blog.update()
        elif (sys.argv[1] == 'update_all'):
            """Also processes the posts"""
            blog.update_all()
    else:
        print 'you suck!' # help?
