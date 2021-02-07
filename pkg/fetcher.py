from head import *


def get_content(url, zh_cn_only = False):
    """
    type url: String
    """
    url = url_decorator(url)
    try:
        req = requests.get(url, headers = headers)
        html = req.text
    except:
        print("Connection failed, please check your VPN setting or restart it, url: " + url)
        return
    soup = BeautifulSoup(html, 'html.parser')
    entire_obj = soup.find('li', attrs = {"class": "chapter entire"})
    if entire_obj:
        link_obj = entire_obj.find('a')
        if link_obj and 'href' in link_obj.attrs:
            # view_adult should before view_full_work else buggy
            url = "https://www.archiveofourown.org" + link_obj.attrs['href'].split('?')[0] + "?view_adult=true?view_full_work=true"
            try:
                req = requests.get(url, headers = headers)
                html = req.text
            except:
                print("Connection failed, please check your VPN setting or restart it, url: " + url)
                return
            soup = BeautifulSoup(html, 'html.parser')
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
    content = content_obj.text.lstrip()
    return content, title
