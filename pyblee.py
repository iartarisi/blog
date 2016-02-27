#!/usr/bin/env python

"""usage: pyblee

Example usage:
    -t "Doomsday Blog" - sets the title
    -p db/newpost - publishes a new post in the set file
"""

import sys
import getopt
import codecs

from bs4 import BeautifulSoup

from blog import Blog
from post import Post
from config import encoding, templatedir, site_type


def usage():
    print(__doc__)


def main():
    try:
        opts, args = getopt.getopt(
            sys.argv[1:], "ht:d:s:p:", ["title", "help", "publish="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit()
        elif opt in ('-p', '--publish'):
            p = Post(arg)
            p.write()
            print('Post/page published, you might want to update now.')

        elif opt in ('-t', '--title'):
            # one-time modification of the template
            f = codecs.open(templatedir+'base.html', 'r', encoding)
            soup = BeautifulSoup(f.read(), 'html.parser')
            f.close()

            tag = soup.find('title')
            tag.contents[0].replaceWith(arg + '${self.title()}')

            tag = soup.find('a', 'title')
            tag.contents[0].replaceWith(arg)

            f = codecs.open(templatedir+'base.html', 'w', encoding)
            f.write(str(soup).decode(encoding))
            f.close()

            print('Title was set to:' + arg)
            sys.exit()
        else:
            assert False, "unhandled option"

    blog = Blog()

    for a in args:
        if a == 'index':
            blog.index()
        elif a == 'archive':
            blog.archive()
    if args == []:
        if site_type == 'blog':
            print("--> Updating your blog")
            blog.update_blog()
        else:
            print("--> Updating your site")
            blog.update_site()

if __name__ == '__main__':
    main()
