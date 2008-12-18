import cgi
from datetime import datetime

from mako.lookup import TemplateLookup

import config

class Rss:
    def __init__(self):
        self.title = config.title
        self.author = config.author
        self.description = cgi.escape(config.description)
        self.link = config.link
        self.language = config.language
        
        now = datetime.strftime(datetime.utcnow(),"%a, %d %b %Y %H:%M:%S GMT")
        self.pub_date = now
        self.pyblee = 'pyBlee!' # FIXME add version information
