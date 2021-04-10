import requests
import bs4
import re
import os
from markdownify import markdownify

def getContent(url):
    content = requests.get(url).content
    main_page = bs4.BeautifulSoup(content,'html.parser')
    content = main_page.find_all("p")
    cnt = ""
    for v in content:
        cnt += str(v).replace("<p> ", "<p>") + "\n"
    mkdn = markdownify(cnt)
    title = main_page.find_all("title")[0].contents[0].lower().replace(" ","_")
    return title, mkdn


def getPrintable(url):
    try:
        main_page_cnt = requests.get(url).content
        main_page = bs4.BeautifulSoup(main_page_cnt,'html.parser')
        main_page = main_page.find_all(class_="heading-navigation")[0]
        return main_page.find_all("a")[0].get('href')
    except Exception as e:
        print("Error getting printable version for: ", url)
        print(e)
        return None

def getLinks(url,articles=True):
    # first get the main page
    main_page_cnt = requests.get(url).content
    main_page = bs4.BeautifulSoup(main_page_cnt,'html.parser')

    tables = main_page.find_all("table")
    if articles:
        for tb in tables:
            if tb.get('class'):
                main_page = tb
    else:
        for tb in tables:
            if not tb.get('class'):
                main_page = tb

    href_arr = []
    entries = [a.find_all("a") for a in main_page.find_all('td')]
    for a in entries:
        for b in a:
            if b.get('href'):
                href_arr.append(b.get('href'))
    return href_arr

printable_arr = []
articles =getLinks("https://www.azleg.gov/constitution/")
for article in articles:
    if 'http' in article:
        printable_arr.append(article)
    else:
        sections = getLinks("https://www.azleg.gov/constitution/" + article,False)
        for section in sections:
            printable_arr.append(getPrintable(section))

articles = {}
for printable in printable_arr:
    try:
        title, cnt = getContent(printable)
        split = re.split("_section|-_", title)
        if not split[0] in articles:
            articles[split[0]]=""
        articles[split[0]] += "\n\n" + cnt
    except Exception as e:
        print(e)
        print("Error for: ", printable)

for name in articles:
    path = "../constitution/" 
    if not os.path.exists(path):
        os.makedirs(path)
    with open((path+ name + ".md"), "w+") as f:
        f.write(articles[name])