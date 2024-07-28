import requests
import time
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
}

def proceed(url, retry_time = 0):
    """
    use link in proceed tag if whole article is not available
    :type url: String
    """
    try:
        req = requests.get(url, headers = headers)
    except:
        req = None
    if not req:
        if retry_time < 2:
            print("request of url " + url + " not found, retry in 30 seconds")
            time.sleep(30)
            return proceed(url, retry_time = retry_time + 1)
        else:
            print("error in url " + url)
            return
    html = req.text
    soup = BeautifulSoup(html, 'html.parser')




    proceed_bar = soup.find_all('ul', attrs = {"class": "actions", "role":"navigation"})
    proceed_item = None
    for item in proceed_bar:
        if len(item.attrs['class']) == 1:
            proceed_item = item
            break
    if not proceed_item:
        print("bug happend")
        return
    link_obj = proceed_item.find_all('a')
    for obj in link_obj:
        if 'href' in obj.attrs and 'works' in obj.attrs['href']:
            url = "https://www.archiveofourown.org" + obj.attrs['href']
            try:
                req = requests.get(url, headers = headers)
                if not req:
                    print("request of proceed url " + url + " not found, retry in 30 seconds")
                    for _ in range(3):
                        time.sleep(30)
                        req = requests.get(url, headers = headers)
                        print("Retry: " + str(_))
                        if req:
                            break
                if not req:
                    print("Fail to connect " + url)
                    return
                html = req.text
                soup = BeautifulSoup(html, 'html.parser')
                if not soup:
                    print("request of proceed url " + url + " not found, retry in 30 seconds")
                    for _ in range(3):
                        time.sleep(30)
                        req = requests.get(url, headers = headers)
                        html = req.text
                        soup = BeautifulSoup(html, 'html.parser')
                        print("Retry: " + str(_))
                        if soup:
                            break
                if not soup:
                    print("error in proceeded url " + url)
                # with open('./temp_html.html', 'w', encoding= 'utf-8') as f:
                #     f.write(html)
                return soup
            except:
                print("Connection failed in proceed, please check your VPN setting or restart it, url: " + url)
                return

def get_content(url, zh_cn_only = False, retry_time = 0):
    """
    :type url: String
    :type zh_cn_only: Bool, only download simplified Chinese articles?
    :retry_time: time already retried
    """
    succeed = True
    raw_url = url
    try:
        req = requests.get(url, headers = headers)
        html = req.text
    except:
        print("Connection failed, please check your VPN setting or restart it, url: " + url)
        succeed = False

    if not succeed:
        return

    if not req:
        print("request of proceed url " + url + " not found, retry in 30 seconds")
        for _ in range(3):
            time.sleep(30)
            req = requests.get(url, headers = headers)
            print("Retry: " + str(_))
            if req:
                break

    soup = BeautifulSoup(html, 'html.parser')
    
    if "If you proceed you have agreed that you are willing to see such content" in html:
        soup = proceed(url)
    # if it is a single chapter,we should use link contains whole chapter
    if not soup:
        return
    


    entire_obj = soup.find('li', attrs = {"class": "chapter entire"})
    if entire_obj:
        link_obj = entire_obj.find('a')
        if link_obj and 'href' in link_obj.attrs:
            url = "https://www.archiveofourown.org" + link_obj.attrs['href']
            
            try:
                req = requests.get(url, headers = headers)
                html = req.text
            except:
                if retry_time < 2:
                    print("Connection failed, retry in 20 seconds")
                    time.sleep(20)
                    get_content(raw_url, zh_cn_only=zh_cn_only, retry_time = retry_time + 1)
                else:
                    print("Connection failed, please check your VPN setting or restart it, url: " + url)
                    succeed = False
            if not succeed:
                return
            if not req:
                print("request of proceed url " + url + " not found, retry in 30 seconds")
                for _ in range(3):
                    time.sleep(30)
                    req = requests.get(url, headers = headers)
                    print("Retry: " + str(_))
                    if req:
                        break
            soup = BeautifulSoup(html, 'html.parser')
            if "If you proceed you have agreed that you are willing to see such content" in html:
                soup = proceed(url)
    if not soup:
        if retry_time < 2:
            print("Rejected by ao3, retry in 120 seconds")
            time.sleep(120)
            get_content(raw_url, zh_cn_only = zh_cn_only, retry_time= retry_time + 1)
        else:
            print(url + " rejected by ao3")
            return
        
    for br in soup.find_all('br'):
        br.insert_before('\n')
        # 处理类似https://www.archiveofourown.org/works/28742886 不显示换行的情况

    for p in soup.find_all('p'):
        p.insert_before('\n')
        # 处理https://archiveofourown.org/works/26447329 不显示换行的情况
    title_obj = soup.find('title')
    # if access denied by ao3(if you download lots of articles, like 50+ articles, ao3 will reject your request and ask you to retry later)
    if not title_obj:
        if "retry" or 'Retry' in html.text and retry_time < 2:
            print("Rejected by ao3, retry in 60 seconds")
            time.sleep(60)
            get_content(raw_url, zh_cn_only = zh_cn_only, retry_time= retry_time + 1)
        else:
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
