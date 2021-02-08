import requests
import bs4
import time
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
}

def get_articles(url, retry_time = 0):
    """
    :type url: String
    :rtype: List[String], article urls in the current page. None if this url is not available at ao3
    """
    succeed = True
    try:
        req = requests.get(url, headers = headers)
        html = req.text
    except:
        succeed = False
    if not succeed:
        if retry_time < 3:
            print(url + " retry in 20 seconds")
            time.sleep(30)
            get_articles(url, retry_time=retry_time + 1)
        else:
            return
    soup = BeautifulSoup(html, 'html.parser')
    
    if "No results found" in soup.text or 'something went wrong' in soup.text:
        return
    urls_obj = soup.find_all('a')
    urls = []
    for item in urls_obj:
        if len(item.attrs) == 1 and 'href' in item.attrs:
            link = item.attrs['href']
            link_list = link.split('/')
            if len(link_list) != 3 or link_list[1] != 'works' or link_list[2].isdigit() == False:
                continue
            url = "https://www.archiveofourown.org"  + link
            urls.append(url)
    return urls

def get_pages(soup):
    """
    :type soup: BeautifulSoup object
    :rtype: (List[String], String), (related pages, current page number). None if it is a single page
    """
    multi_page = False
    for tag in ["previous", "next"]:
        has_multi_page = soup.find('li', attrs = {"class": tag})
        if has_multi_page:
            multi_page = True
            # break to save time, it is faster than attrs = {"class": ["previous", "next"]}
            break
    # if have no relative links
    if not multi_page:
        return
    # find navigation bar for analyze
    navigation = soup.find('ol', attrs = {"role": "navigation"})
    # maximum pages related
    mx_page = 0
    # standard url of related pages
    standard_format = None
    # pagenumber of current page
    curpage = None
    for item in navigation:
        # check if it is an element object
        if isinstance(item, bs4.element.Tag) == False:
            continue
        
        if not curpage:
            cur = item.find('span', attrs = {"class": "current"})
            if cur and cur.text.isnumeric():
                curpage = cur.text
        pg = item.find("span")
        if pg is not None and pg.text.isnumeric():
            mx_page = pg.text

        hrefs = item.findAll("a")
        
        for hr in hrefs:
            if not standard_format and 'href' in hr.attrs:
                standard_format = hr.attrs['href']
            if hr.text.isnumeric():
                mx_page = hr.text
    
    if not standard_format:
        print("Cannot find standard link format, please email the link with error to yilingliu1994@gmail.com")
        exit(0)

    mx_page = int(mx_page) + 1
    standard_format = "https://archiveofourown.org" + standard_format
    page_loc = standard_format.find("page=") + len("page=")
    end_loc = page_loc
    while end_loc < len(standard_format) and standard_format[end_loc].isnumeric():
        end_loc += 1
    prefix = standard_format[:page_loc]
    suffix = standard_format[end_loc:]
    related_urls = []
    for i in range(1, mx_page):
        cururl = prefix + str(i) + suffix
        related_urls.append(cururl)
    
    return related_urls, curpage

# def utest(path = './test3.html'):
#     with open(path, 'rb') as f:
#         text = f.read()
#     soup = bs4.BeautifulSoup(text)
#     a = get_pages(soup)
#     print(a)
#     b = get_articles(soup)
#     print(b)
