import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
}

def proceed(soup):
    proceed_bar = soup.find_all('ul', attrs = {"class": "actions", "role":"navigation"})
    proceed = None
    for item in proceed_bar:
        if len(item.attrs['class']) == 1:
            proceed = item
            break
    if not proceed:
        print("bug happend")
        return
    link_obj = proceed.find_all('a')
    for obj in link_obj:
        if 'href' in obj.attrs and 'works' in obj.attrs['href']:
            url = "https://www.archiveofourown.org" + obj.attrs['href']
            try:
                req = requests.get(url, headers = headers)
                html = req.text
                soup = BeautifulSoup(html, 'html.parser')
                with open('./temp_html.html', 'w', encoding= 'utf-8') as f:
                    f.write(html)
                return soup
            except:
                print("Connection failed, please check your VPN setting or restart it, url: " + url)
                return

def get_content(url, zh_cn_only = False):
    """
    type url: String
    """
    try:
        req = requests.get(url, headers = headers)
        # cookies = requests.utils.dict_from_cookiejar(req.cookies)
        # req = requests.get(req.url, headers = headers, cookies = cookies)
        html = req.text
    except:
        print("Connection failed, please check your VPN setting or restart it, url: " + url)
        return
    soup = BeautifulSoup(html, 'html.parser')
    if "If you proceed you have agreed that you are willing to see such content" in html:
        soup = proceed(soup)
    
    entire_obj = soup.find('li', attrs = {"class": "chapter entire"})
    if entire_obj:
        link_obj = entire_obj.find('a')
        if link_obj and 'href' in link_obj.attrs:
            url = "https://www.archiveofourown.org" + link_obj.attrs['href']
            
            try:
                req = requests.get(url, headers = headers)
                html = req.text
            except:
                print("Connection failed, please check your VPN setting or restart it, url: " + url)
                return
            soup = BeautifulSoup(html, 'html.parser')
            if "If you proceed you have agreed that you are willing to see such content" in html:
                soup = proceed(soup)
    # with open('./temp_html.html', 'w', encoding= 'utf-8') as f:
    #     f.write(html)
    title_obj = soup.find('title')
    if not title_obj:
        print(url + " does not have a standard title")
        return
    title = title_obj.text.strip()
    print("Downloading " + title + " from " + url)
    if zh_cn_only:
        language_obj = soup.find('dd', {"class": "language"})
        if not language_obj or "中文" not in language_obj.text:
            print(url + " is not written in Chinese")
            return
    content_obj = soup.find('div', attrs = {"id":"workskin"})
    if not content_obj:
        print("Page error, url:" + url)
        return
    content = content_obj.text.lstrip()
    return content, title

