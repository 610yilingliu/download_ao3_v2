import os
import sys
import time

from pkg.router import *
from pkg.fetcher import *
from pkg.gpt_helper import GPTHelper


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
    if os.path.isfile(fname):
        print('------------------------' + fname + ' already exists -------------------------')
        return
    with open(fname, 'w', encoding= 'utf-8') as f:
        f.write(content)

def dl_conbined(articles, gpt = None, cp = None):
    """
    type articles: List[String] or None
    rtype: int, number of articles downloaded
    """
    cnt = 0
    if articles:
        for article in articles:
            returned_item = get_content(article, zh_cn_only= zhcn_only)
            if returned_item:
                content, title = returned_item
                if gpt is not None:
                    gpt.import_text(content)
                    score = gpt.judgement(cp)
                    if float(score) < 0.2:
                        print("文章与CP关联度不高或有拆逆，跳过")
                        continue
                    else:
                        write_file(title, content, folder_name)
                        cnt += 1
                # success count + 1
                else:
                    write_file(title, content, folder_name)
                    cnt += 1
    return cnt     

class Logger(object):
    """
    Logging module
    """
    def __init__(self, filename, stream=sys.stdout):
        self.terminal = stream
        self.log = open(filename, "wb", buffering=0)

    def write(self, *message):
        message = ",".join([str(it) for it in message])
        self.terminal.write(str(message))
        prefix = '[' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ']'
        self.log.write(prefix.encode('utf-8') + str(message).encode('utf-8'))

    def flush(self):
        pass

def time_helper(seperator = '_', to_sec = True):
    """
    return a string like 2020_09_11_22_43_00 (if to_sec is True) or 2020_09_11_22_43 (if to_sec is False)
    """
    if to_sec:
        return time.strftime("%Y" + seperator + "%m" + seperator + "%d" + seperator + "%H" + seperator + "%M" + seperator + "%S", time.localtime()) 
    return time.strftime("%Y" + seperator + "%m" + seperator + "%d" + seperator + "%H" + seperator + "%M", time.localtime()) 

if __name__ == '__main__':
    # how many articles downloaded
    gpt_on = False
    if gpt_on == True:
        print("测试功能，使用GPT检查文章是否有它人乱入CP/逆CP行为.请新建.env文件，内容为OPENAI_API_KEY = 你的api key，非程序员请无视，本功能默认关闭（前一行gpt_on = False）")
        cp = input("输入目标CP（两个字，如旬宴）: ")
        gpt = GPTHelper(api_key = os.getenv("OPENAI_API_KEY"))

    article_cnt = 0
    # logging
    if not os.path.exists('./log'):
        os.mkdir('./log')
    start_time = time_helper()
    sys.stdout = Logger('./log/' + start_time + '.log')

    print("Cannot be used in mainland China, please use a VPN with global mode or ask someone overseas to help you")
    print("All comments are written in English, some machines cannot print simplified Chinese on console")
    print("Please paste an AO3 url here:  ")
    url = input()
    print("Your option is " + url)
    print("Simplified Chinese only?(Y if yes else press anything else): ")
    zhcn_only = input()
    print("Your option is " + zhcn_only)
    if zhcn_only == 'y' or zhcn_only == 'Y':
        zhcn_only = True
    else:
        zhcn_only = False
    # check if the input folder name is valid in Windows
    valid = False
    while valid == False:
        valid = True
        print("Input a folder name to store downloaded file: ")
        folder_name = input()
        print("Your option is " + folder_name)
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
    url = url.lstrip()
    option_1 = url.startswith("https://archiveofourown.org") 
    option_2 = url.startswith("https://www.archiveofourown.org")
    if option_1 == False and option_2 == False:
        print("Please use url starts with \'https://archiveofourown.org/\' or \'https://www.archiveofourown.org/\'")
        exit(0)
    print("Process started, connecting to the website...if connection failed or it is too slow, please check if you have pyopenssl in your environment")
    
    try:
        req = requests.get(url, headers = headers)
        html = req.text
        print("connection established")
    except:
        print("Cannot visit the url you pasted, please check your internet or VPN settings")
        exit(0)
    if not req:
        print("request of url " + url + " not found")
        exit(0)
    # single article
    if is_article(url):
        returned_item = get_content(url, zh_cn_only= zhcn_only)
        if returned_item:
            content, title = returned_item
            write_file(title, content, folder_name)
            article_cnt += 1

    else:
        soup = BeautifulSoup(html, 'html.parser')
        # get a list of pages to download
        page_detail = get_pages(soup)
        if page_detail:
            urls, curpage = page_detail
            page_amount = len(urls)
            print(str(page_amount) + " related pages detected, current page index is " + curpage + ", do you want to download all pages? Page index from 1 to " + str(page_amount))
            print("press key a to download all, press s to select start and and index, press other keys to download articles in the current page ")
            argument = input()
            print("Your option is " + argument)
            # download all related pages
            if argument == 'a' or argument == 'A':
                for url in urls:
                    articles = get_articles(url)
                    if gpt_on == False:
                        article_cnt += dl_conbined(articles, gpt = None)
                    else:
                        article_cnt += dl_conbined(articles, gpt = gpt, cp = cp)
            # download page from a range
            elif argument == 's' or argument == 'S':
                start = None
                end = None
                while not start or not end:
                    print("Start: ")
                    start = input()
                    print("The start page you choose is " + start)
                    print("End: ")
                    end = input()
                    print("The end page you choose is " + end)
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
                    article_cnt += dl_conbined(articles)
            # current page only
            else:
                url = urls[int(curpage) - 1]
                articles = get_articles(url)
                if gpt_on == False:
                    article_cnt += dl_conbined(articles, gpt = None)
                else:
                    article_cnt += dl_conbined(articles, gpt = gpt, cp = cp)
        else:
            articles = get_articles(url)
            if gpt_on == False:
                article_cnt += dl_conbined(articles, gpt = None)
            else:
                article_cnt += dl_conbined(articles, gpt = gpt, cp = cp)
    print(str(article_cnt) + ' articles downloaded')
    print("Download Finished, if you cannot find the text file in that folder, please close simplified Chinese only option")
    print("Press any key to close the program")
    input()
    