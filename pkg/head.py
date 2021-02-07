import requests
import bs4
from bs4 import BeautifulSoup
from router import *
from fetcher import *


headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    }

def url_decorator(url):
    """
    add permission to avoid access restriction
    :type url: String, link with/without adult suffix
    """
    if not url.endswith('?view_adult=true'):
        url += '?view_adult=true'
    return url

