import requests
import bs4
from bs4 import BeautifulSoup

def url_decorator(url):
    """
    add permission to avoid access restriction
    :type url: String, link with/without adult suffix
    """
    if not url.endswith('?view_adult=true'):
        url += '?view_adult=true'
    return url




