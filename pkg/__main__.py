import os
import sys
import time

from head import *
from router import *
from fetcher import *

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
}


def is_article(url):
    """
    tell if an url is a single article, True if yes else False
    :type url: String
    :rtype: Bool
    """
    # remove https://
    url = url[8:]
    url_split = url.split('/')
    if url_split[1] == 'works' and url_split[2].isdigit():
        return True
    return False

def write_file(title, content, folder_name):
    """
    :type title: String
    :content: String
    :folder_name: String
    """
    win_invalid_chars = "\\/:*?\"<>|"
    name = ""
    for char in title:
        if char in win_invalid_chars:
            name += '_'
        else:
            name += char
    fname = './' + folder_name + '/' + name + '.txt'
    with open(fname, 'w', encoding= 'utf-8') as f:
        f.write(content)

def dl_conbined(articles):
    """
    type articles: List[String] or None
    """
    if articles:
        for article in articles:
            returned_item = get_content(article, zh_cn_only= zhcn_only)
            if returned_item:
                content, title = returned_item
                write_file(title, content, folder_name)

class Logger(object):
    def __init__(self, filename, stream=sys.stdout):
	    self.terminal = stream
	    self.log = open(filename, "wb", buffering=0)

    def write(self, *message):
        message = ",".join([str(it) for it in message])
        self.terminal.write(str(message))
        self.log.write(str(message).encode('utf-8'))

    def flush(self):
        pass

def time_helper(seperator = '_', to_sec = True):
    """
    return a string like 2020_09_11_22_43_00 (if to_sec is True) or 2020_09_11_22_43 (if to_sec is False)
    """
    localtime = time.asctime(time.localtime(time.time()))
    if to_sec:
        return time.strftime("%Y" + seperator + "%m" + seperator + "%d" + seperator + "%H" + seperator + "%M" + seperator + "%S", time.localtime()) 
    return time.strftime("%Y" + seperator + "%m" + seperator + "%d" + seperator + "%H" + seperator + "%M", time.localtime()) 

if __name__ == '__main__':
    start_time = time_helper('-')
    if not os.path.exists('./update_log'):
        os.mkdir('./update_log')
    sys.stdout = Logger('./update_log/' + start_time + '.log')
    print("Start time:" + start_time)
    print("Cannot be used in mainland China, please use a VPN with global mode or ask someone overseas to help you")
    print("All comments are written in English, some machines cannot print simplified Chinese on console")

    url = input('Please paste an AO3 url here:  ')
    zhcn_only = input("Simplified Chinese only?(Y if yes else press anything else): ")
    if zhcn_only == 'y' or zhcn_only == 'Y':
        zhcn_only = True
    else:
        zhcn_only = False
    valid = False
    while valid == False:
        valid = True
        folder_name = input("Input a folder name to store downloaded file: ")
        win_invalid_chars = "\\/:*?\"<>|"
        for char in folder_name:
            if char in win_invalid_chars:
                print("Please check the folder name you want to use, input again")
                valid = False
                break

    curpath = os.getcwd()
    print("Articles will be stored in " + curpath + '\\' + folder_name)
    if not os.path.exists('./' + folder_name):
        os.mkdir('./' + folder_name)
    url = url.rstrip('/')
    if not url.startswith("https://archiveofourown.org/"):
        print("Please use url starts with \'https://archiveofourown.org/\'")
        exit(0)
    print("Process started, connecting to the website...")
    try:
        req = requests.get(url, headers = headers)
        html = req.text
    except:
        print("Cannot visit the url you pasted, please check your internet or VPN settings")
        exit(1)

    if is_article(url):
        returned_item = get_content(url, zh_cn_only= zhcn_only)
        if returned_item:
            content, title = returned_item
            write_file(title, content, folder_name)

    else:
        soup = BeautifulSoup(html, 'html.parser')
        # get a list of pages to download
        page_detail = get_pages(soup)
        if page_detail:
            urls, curpage = page_detail
            page_amount = len(urls)
            print(str(page_amount) + " related pages detected, current page index is " + curpage + ", do you want to download all pages? Page index from 1 to " + str(page_amount))
            argument = input("press key a to download all, press s to select start and and index, press other keys to download articles in the current page ")
            if argument == 'a' or argument == 'A':
                for url in urls:
                    articles = get_articles(url)
                    dl_conbined(articles)
            elif argument == 's' or argument == 'S':
                start = None
                end = None
                while not start or not end:
                    start = input("Start: ")
                    end = input("End: ")
                    if start.isdecimal() == False or end.isdecimal() == False:
                        print("Please input number for start and end index, input again")
                        start, end = None, None
                        continue
                    start, end = int(start), int(end)
                    if start < 1 or start > page_amount or end < 1 or end > page_amount or start > end:
                        print("Invalid page number, start should smaller or equal to end, input again")
                        start, end = None, None
                        continue
                start = start - 1
                for i in range(start, end):
                    url = urls[i]
                    articles = get_articles(url)
                    dl_conbined(articles)
            else:
                url = urls[int(curpage) - 1]
                articles = get_articles(url)
                dl_conbined(articles)
    end_time = time_helper('-')
    print("End time:" + end_time)
    print("Download Finished, if you cannot find the text file in that folder, please close simplified Chinese only option")
    input("Press any key to close the program")
    
    