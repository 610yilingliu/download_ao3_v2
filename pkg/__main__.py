import os

from head import *


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

if __name__ == '__main__':
    print("Cannot be used in mainland China, please use a VPN with global mode or ask someone overseas to help you")
    print("All comments are written in English, some machines cannot print simplified Chinese on console")

    url = input('lease paste an AO3 url here:  ')
    zhcn_only = input("Simplified Chinese only?(Y if yes else press anything else): ")
    if zhcn_only == 'y' or 'Y':
        zhcn_only = True
    else:
        zhcn_only = False

    while True:
        valid = True
        folder_name = input("Input a folder name to store downloaded file: ")
        win_invalid_chars = "\\/:*?\"<>|"
        for char in folder_name:
            if char in win_invalid_chars:
                print("Please check the folder name you want to use, input again")
                valid = False
        if valid:
            break

    curpath = os.getcwd()
    print("Articles will be stored in" + curpath + '\\\\' + folder_name)
    url = url.rstrip('/')
    if not url.startswith("https://archiveofourown.org/"):
        print("Please use url starts with \'https://archiveofourown.org/\'")
        exit(0)
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
            print(str(page_amount) + "of related pages detected, current page index is" + curpage + ", do you want to download all pages? Page index from 1 to" + str(1 + int(page_amount)))
            argument = input("press key a to download all, press s to select start and and index, press other keys to download articles in the current page")
            if argument == 'a':
                for url in urls:
                    articles = get_articles(url)
                    for article in articles:
                        returned_item = get_content(article, zh_cn_only= zhcn_only)
                        if returned_item:
                            content, title = returned_item
                            write_file(title, content, folder_name)
            elif argument == 's':
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
                    url = url[i]
                    articles = get_articles(url)
                    for article in articles:
                        returned_item = get_content(article, zh_cn_only= zhcn_only)
                        if returned_item:
                            content, title = returned_item
                            write_file(title, content, folder_name)
            else:
                url = urls[int(curpage) - 1]
                articles = get_articles(url)
                for article in articles:
                    returned_item = get_content(article, zh_cn_only= zhcn_only)
                    if returned_item:
                        content, title = returned_item
                        write_file(title, content, folder_name)
    print("Download Finished, if you cannot find the text file in that folder, please close simplified Chinese only option")
    input("Press any key to close the program")
    
    