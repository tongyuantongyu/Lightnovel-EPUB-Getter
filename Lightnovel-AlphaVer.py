# coding:utf-8

import requests
from bs4 import BeautifulSoup
import bs4
from multiprocessing.dummy import Pool as tp
import os
import re
from ebooklib import epub
import base64
import zipfile

pool = tp(processes=16)
dirn = os.getcwd()
hd = {'User-Agent': 'Mozilla/5.0 (MSIE 9.0; Windows NT 6.1; Trident/5.0)'}
p = {"http": "http://127.0.0.1:8089"}
style = b'CkBuYW1lc3BhY2UgZXB1YiAiaHR0cDovL3d3dy5pZHBmLm9yZy8yMDA3L29wcyI7CmJvZHkgewogICAgZm9udC1mYW1pbHk6IENhbWJyaWEsIExpYmVyYXRpb24gU2VyaWYsIEJpdHN0cmVhbSBWZXJhIFNlcmlmLCBHZW9yZ2lhLCBUaW1lcywgVGltZXMgTmV3IFJvbWFuLCBzZXJpZjsKfQpoMiB7CiAgICAgdGV4dC1hbGlnbjogbGVmdDsKICAgICB0ZXh0LXRyYW5zZm9ybTogdXBwZXJjYXNlOwogICAgIGZvbnQtd2VpZ2h0OiAyMDA7ICAgICAKfQpvbCB7CiAgICAgICAgbGlzdC1zdHlsZS10eXBlOiBub25lOwp9Cm9sID4gbGk6Zmlyc3QtY2hpbGQgewogICAgICAgIG1hcmdpbi10b3A6IDAuM2VtOwp9Cm5hdltlcHVifHR5cGV+PSd0b2MnXSA+IG9sID4gbGkgPiBvbCAgewogICAgbGlzdC1zdHlsZS10eXBlOnNxdWFyZTsKfQpuYXZbZXB1Ynx0eXBlfj0ndG9jJ10gPiBvbCA+IGxpID4gb2wgPiBsaSB7CiAgICAgICAgbWFyZ2luLXRvcDogMC4zZW07Cn0K'
cookies = {
    'UM_distinctid': '15b3343e4ed121-0165da3fda7694-635c7229-13c680-15b3343e4ee1ba',
    'lightnovel_0a3d_secqaaS0': '58443HIDJwj1Z0JRlmJ%2F1F9XU5Rog%2FQ2doFGId%2BiqkbOb6DALD8MwpkjuvYhE1IEA19ekDAhdADW9ERh8sDqYc2lpm%2Brqk%2FwwuohStbM%2Bsj3lXLs',
    'lightnovel_0a3d_seccodeS0': '1dbfbQKkuU3FVUwoc0E%2FRtdkU%2BwaIcvvj84eO2RWA03aLm7H3MtI5ZtOd7R7reXGmySEqZK0iEY',
    'lightnovel_0a3d_auth': '0b30SitOmA5o9Rey03QhLjvJztGFoED9yF88O0ywSqV8qzsbsFAjAF96%2FB92i1zoNdKndFi3WYxS7q5Z9QT7r6p8iwM',
    'CNZZDATA3599420': 'cnzz_eid%3D289966699-1475927145-%26ntime%3D1491211360'
}


def getpage(link):
    i = 0
    while i < 3:
        try:
            gethtml = requests.get(link, headers=hd, cookies=cookies)
            if gethtml.status_code == 200:
                break
            else:
                i += 1
        except:
            i += 1
    Soup = BeautifulSoup(gethtml.content, 'lxml')
    return Soup


def getpic(link):
    i = 0
    while i < 3:
        try:
            getfile = requests.get(link, headers=hd)
            if getfile.status_code == 200:
                break
            else:
                i += 1
        except:
            i += 1
    return getfile.content


def genlink(tid, page=1, authorid=None):
    l1 = 'https://www.lightnovel.us/forum.php?mod=viewthread'
    l2 = '&tid='
    l3 = '&page='
    l4 = '&authorid='
    link = l1 + l2 + tid + l3 + str(page)
    if authorid is not None:
        link = link + l4 + authorid
    return link


def goodtitle(title):
    return title.replace(' ', '').replace('：', '').replace(':', '').replace('|', '_').replace('"', '_').replace('/', '_').replace('?', '_').replace('*', '_').replace('<', '_').replace('>', '_').replace(';', '')


class LightPage:
    def __init__(self, link):
        print('开始...')
        self.link = link
#        self.get_info()
#        self.get_all()
#        self.get_posts()
#        self.find_picture()
#        self.get_picture()
#        self.gen_page()
#        self.gen_book()

    def get_info(self):
        print('读取网页信息...')
        self.tid = re.findall('(?<=thread-)\\d+(?=-)', self.link)[0]
        self.page = getpage(genlink(self.tid))
        self.content = [self.page]
        try:
            self.pagenum = int(re.findall('\\d+', self.page.find('span', title=re.compile('共 \\d+ 页')).get_text())[0])
        except AttributeError:
            self.pagenum = 1
        self.title = self.page.find('span', id='thread_subject').get_text()
        self.authorid = re.findall('(?<=space-uid-)\\d+', self.page.find('div', class_='authi').find('a')['href'])[0]

    def get_all(self):
        print('获取所有页面...')
        if self.pagenum == 1:
            pass
        else:
            for i in range(2, self.pagenum + 1):
                link = genlink(self.tid, i, self.authorid)
                self.content.append(getpage(link))

    def get_posts(self):
        print('筛选回复...')
        self.posts = []
        if len(self.content) != self.pagenum:
            self.get_all()
        for i in self.content:
            self.posts = self.posts + i.find_all('td', class_='t_f')

    def find_picture(self):
        print('筛选图片...')
        self.picturetag = []
        for i in self.posts:
            self.picturetag.append(i.find_all('img'))

    def get_picture(self):
        print('获取图片...')
        self.picturelink = []
        for i in self.picturetag:
            for j in i:
                try:
                    l = j['file']
                    if l[:4] != 'http':
                        l = 'https://www.lightnovel.us/' + l
                    self.picturelink.append(l)
                except KeyError:
                    l = j['src']
                    if l[:4] != 'http':
                        l = 'https://www.lightnovel.us/' + l
                    self.picturelink.append(l)
        picture = pool.map(getpic, self.picturelink)
        self.picture = [(self.picturelink[i].split('/')[-1], picture[i]) for i in range(len(picture))]

    def gen_page(self):
        print('生成页面...')
        self.ppages = []
        for i in range(len(self.posts)):
            p = self.posts[i]
            main = p.prettify()
            if len(main) > 900:
                main = re.sub(r'<i.*</i>', '', main)
                for j in self.picturetag[i]:
                    h = j.prettify()
                    f = j['file'].split('/')[-1]
                    g = '<p>' + f + '</p>'
                    main = main.replace(h, g)
                lti = '第' + str(i + 1) + '章'
                main = BeautifulSoup(main, 'lxml').get_text().split('\n')
                main = '\n'.join(['<p>' + l + '</p>\n' for l in main])
                for j in self.picturetag[i]:
                    f = j['file'].split('/')[-1]
                    g = '<p>' + f + ' </p>\n'
                    h = '<p><img src="images/' + f + '"/></p>\n'
                    main = main.replace(g, h)
                ht = '<html>\n<head>\n<title>章节' + lti + '</title>\n</head>\n<body>\n<div>\n<h2>' + lti + '</h3>\n' + main + '</div>\n</body>\n</html>'
                self.ppages.append((str(i + 1), lti, ht))

    def gen_book(self):
        print('生成文件...')
        self.book = epub.EpubBook()
        self.book.set_identifier(self.authorid)
        self.book.set_title(self.title)
        self.book.set_language('zh')
        self.book.add_author("TYTY's Python LightNovel Epub Maker")
        self.bookcon = [epub.EpubHtml(title=i[1], file_name=i[0] + '.xhtml', content=i[2], lang='zh_cn') for i in self.ppages]
        for i in self.bookcon:
            self.book.add_item(i)
        self.book.toc = [epub.Link(i.file_name, i.title, i.file_name.replace('.xhtml', '')) for i in self.bookcon]
        self.book.add_item(epub.EpubNcx())
        self.book.add_item(epub.EpubNav())
        dstyle = str(base64.b64decode(style))
        css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=dstyle)
        self.book.add_item(css)
        self.book.spine = ['nav'] + self.bookcon
        self.filename = goodtitle(self.title + '.epub')
        epub.write_epub(self.filename, self.book, {})
        self.epubzip = zipfile.ZipFile(self.filename, 'a')
        for i in self.picture:
            self.epubzip.writestr('EPUB/images/' + i[0], i[1])
        self.epubcontent = self.epubzip.read('EPUB/content.opf')

    def correct_content(self):
        linelist = []
        for i in range(len(self.picture)):
            picname = self.picture[i][0]
            picformat = picname.split('.')[-1]
            if picformat == 'jpg':
                picformat = 'jpeg'
            line = '    <item href="images/' + picname + '" id="picture_' + str(i) + '" media-type="image/' + picformat + '"/>\n'
            linelist.append(line)
        self.epubcontent = self.epubcontent.decode().replace('  <manifest>\n', '  <manifest>\n' + ''.join(linelist)).encode()
        tempzip = zipfile.ZipFile('temp', 'w', zipfile.ZIP_DEFLATED)
        for i in self.epubzip.infolist():
            if i.filename != 'EPUB/content.opf':
                buffer = self.epubzip.read(i.filename)
                tempzip.writestr(i, buffer)
        tempzip.writestr('EPUB/content.opf', self.epubcontent)
        self.epubzip.close()
        tempzip.close()
        os.remove(self.filename)
        os.rename('temp', self.filename)


if __name__ == '__main__':
    link = input('输入网页地址: ')
    page = LightPage(link)
    page.get_info()
    page.get_all()
    page.get_posts()
    page.find_picture()
    page.get_picture()
    page.gen_page()
    page.gen_book()
    page.correct_content()
    print('完成')
