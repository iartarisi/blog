import sys
import os

from blog import Blog
from post import Post

blog = Blog()
if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == 'post':
            post = Post(sys.argv[2])
            post.write()
            blog.update()
    elif len(sys.argv) == 2:
        if (sys.argv[1] == 'index' or sys.argv[1] == 'archive'):
            blog.write(sys.argv[1])
        elif (sys.argv[1] == 'update'):
            blog.update()
    else:
        print 'you suck!' # help?
