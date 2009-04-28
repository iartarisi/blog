import cgi
from datetime import datetime

from mako.lookup import TemplateLookup

import config
import pytz

class Rss:
    def __init__(self):
        self.title = config.title
        self.author = config.author
        self.description = cgi.escape(config.description)
        self.link = config.link
        self.language = config.language
        
        eurbuc = pytz.timezone("Europe/Bucharest")
        now = datetime.strftime(datetime.now(eurbuc),
                                "%a, %d %b %Y %H:%M:%S %z")
        self.pub_date = now
        self.pyblee = 'pyBlee!' # FIXME add version information
