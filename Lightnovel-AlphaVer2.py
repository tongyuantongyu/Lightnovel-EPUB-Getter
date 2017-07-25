# coding:utf-8

import requests
from bs4 import BeautifulSoup
import bs4
from multiprocessing.dummy import Pool as tp
import os
import re
from ebooklib import epub
import zipfile
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
pool = tp(processes=16)
dirn = os.getcwd()
hd = {'User-Agent': 'Mozilla/5.0 (MSIE 9.0; Windows NT 6.1; Trident/5.0)'}
p = {"http": "http://127.0.0.1:8089", "https": "https://127.0.0.1:8089"}
cookies = {
}


class Css:
    def __init__(self):
        self.stylelist = []
        self.styletable = dict()
        self.stylenum = 0

    def add_style(self, prop):
        if prop in self.stylelist:
            return self.styletable[prop]
        else:
            self.stylenum += 1
            self.stylelist.append(prop)
            self.styletable[prop] = self.stylenum
            return self.stylenum

    def make_css(self):
        self.css = ''
        for i in self.stylelist:
            j = self.styletable[i]
            style = '.style' + str(j) + ' {\n'
            k = i.split(' ')
            if k[0] != '0':
                style = style + 'color: ' + k[0] + ';\n'
            if k[1] != '0':
                style = style + 'font-size: ' + k[1] + ';\n'
            if k[2] == '1':
                style = style + 'font-weight:bold;\n'
            style = style + '}\n'
            self.css = self.css + style
        return self.css


class PictureList:
    def __init__(self):
        self.piclist = []
        self.pictable = dict()
        self.picdown = []
        self.picnum = 0

    def add_picture(self, url):
        if url in self.piclist:
            return self.pictable[url]
        else:
            self.picnum += 1
            self.piclist.append(url)
            self.pictable[url] = self.picnum
            return self.picnum

    def down_picture(self):
        for i in self.pictable:
            if len(i) < 29:
                url = i
            elif i[:29] == 'forum.php?mod=attachment&aid=':
                url = 'https://www.lightnovel.us/' + i
            else:
                url = i
            self.picdown.append((str(self.pictable[i]), url))
        self.pic = pool.map(getpic, self.picdown)
        return self.pic


class RPage:
    def __init__(self, num, title, con):
        self.n = num
        self.t = title
        self.c = con


css = Css()
picl = PictureList()


def getpage(link):
    i = 0
    while i < 3:
        try:
            gethtml = requests.get(link, headers=hd, proxies=p, cookies=cookies, verify=False)
            if gethtml.status_code == 200:
                Soup = BeautifulSoup(gethtml.content, 'lxml')
                return Soup
                break
            else:
                i += 1
        except:
            i += 1


def getpic(inpack):
    link = inpack[1]
    i = 0
    while i < 3:
        try:
            getfile = requests.get(link, headers=hd, proxies=p, verify=False)
            if getfile.status_code == 200:
                return (inpack[0], getfile.content)
                break
            else:
                i += 1
        except:
            i += 1


def post_filter(page):
    reply_list = page.find_all('td', class_='t_f')
    filter_reply = [i for i in reply_list if len(i.get_text()) > 250]
    return filter_reply


def firstf_process(reply):
    # 轻国贴子的主楼有一个很诡异的</br>标签bs难以解析，需要特殊处理。
    content = [i for i in list(reply)[2:] if str(i) != '<br/>']
    line = []
    for i in content:
        if '</' not in str(i) and '/>' not in str(i):
            j = str(i).split('\n')
            k = '<p>' + '</p>\n<p>'.join(j) + '</p>\n'
            line.append(k)
        elif 'font' in str(i):
            j = str(i).split('\n')
            for k in j:
                text = BeautifulSoup(k, 'lxml').get_text()
                if 'font color=' in k:
                    l = k.find('font color=')
                    global colorstring
                    colorstring = k[l+13:l+19]
                    colorstring = re.findall(r'[0-9a-fA-F]{3,6}', colorstring)[0]
                else:
                    colorstring = '0'
                if 'font size=' in k:
                    l = k.find('font size=')
                    global sizestring
                    sizestring = k[l+11:l+12]
                else:
                    sizestring = '0'
                if '<strong>' in k:
                    global bold
                    bold = '1'
                else:
                    bold = '0'
                style = colorstring + ' ' + sizestring + ' ' + bold
                cssid = css.add_style(style)
                m = '<p class="style' + str(cssid) + '">' + text + '</p>\n'
                line.append(m)
        elif 'img' in str(i):
            try:
                url = i.find('img')['file']
            except TypeError:
                url = i['file']
            pid = picl.add_picture(url)
            picf = url.split('.')[-1]
            if url[:5] == 'forum':
                picf = 'jpg'
            elif len(picf) > 4:
                picf = 'jpg'
            j = '<div><img alt="" src="images/' + str(pid) + '.' + picf + '" /></div>\n'
            line.append(j)
    title = BeautifulSoup(line[0], 'lxml').get_text()
    fline = []
    head = '<html>\n<head>\n<link href="style/nav.css" rel="stylesheet" type="text/css"/>\n<title>' + title + '</title>\n</head>\n'
    fline.append(head)
    bodyfirst = '<body>\n<div>\n<h2>' + title + '</h2>\n'
    fline.append(bodyfirst)
    line = fline + line[1:]
    line.append('</div>\n</body>\n</html>')
    return (title, ''.join(line))


def otherf_process(reply):
    content = [i for i in list(reply)[2:] if str(i) != '<br/>' if str(i) != '/n']
    line = []
    for i in content:
        if '</' not in str(i) and '/>' not in str(i):
            j = str(i).split('\n')
            k = '<p>' + '</p>\n<p>'.join(j) + '</p>\n'
            line.append(k)
        elif 'div' in str(i):
            text = i.get_text()
            j = str(i)
            if 'font color=' in j:
                l = i.find('font color=')
                colorstring = j[l+13:l+19]
            else:
                colorstring = '0'
            if 'font size=' in j:
                l = j.find('font size=')
                sizestring = j[l+11:l+12]
            else:
                sizestring = '0'
            if '<strong>' in j:
                bold = '1'
            else:
                bold = '0'
            style = colorstring + ' ' + sizestring + ' ' + bold
            cssid = css.add_style(style)
            m = '<p class="style' + str(cssid) + '">' + text + '</p>\n'
            line.append(m)
        elif 'img' in str(i):
            url = i.find('img')['file']
            pid = picl.add_picture(url)
            picf = url.split('.')[-1]
            if url[:5] == 'forum':
                picf = 'jpg'
            elif len(picf) > 4:
                picf = 'jpg'
            j = '<div><img alt="" src="images/' + str(pid) + '.' + picf + '" /></div>\n'
            line.append(j)
    title = BeautifulSoup(line[0], 'lxml').get_text()
    fline = []
    head = '<html>\n<head>\n<link href="style/nav.css" rel="stylesheet" type="text/css"/>\n<title>' + title + '</title>\n</head>\n'
    fline.append(head)
    bodyfirst = '<body>\n<div>\n<h2>' + title + '</h2>\n'
    fline.append(bodyfirst)
    line = fline + line[1:]
    line.append('</div>\n</body>\n</html>')
    return (title, ''.join(line))


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
        self.get_info()
        self.get_all()
        self.filt_posts()
        self.make_page()
        self.gen_book()

    def get_info(self):
        print('读取网页信息...')
        self.tid = re.findall('(?<=thread-)\\d+(?=-)', self.link)[0]
        self.page = getpage(genlink(self.tid))
        self.title = self.page.find('span', id='thread_subject').get_text()
        self.authorid = re.findall('(?<=space-uid-)\\d+', self.page.find('div', class_='authi').find('a')['href'])[0]

    def get_all(self):
        print('获取所有页面...')
        self.page = getpage(genlink(self.tid, 1, self.authorid))
        self.content = [self.page]
        try:
            self.pagenum = int(re.findall('\\d+', self.page.find('span', title=re.compile('共 \\d+ 页')).get_text())[0])
        except AttributeError:
            self.pagenum = 1
        if self.pagenum != 1:
            for i in range(2, self.pagenum + 1):
                link = genlink(self.tid, i, self.authorid)
                self.content.append(getpage(link))

    def filt_posts(self):
        self.reply = []
        for i in self.content:
            self.reply = self.reply + post_filter(i)

    def make_page(self):
        self.bookpages = []
        pnum = 1
        for i in self.reply:
            if pnum == 1:
                title, con = firstf_process(i)
                self.bookpages.append(RPage(pnum, title, con))
                pnum += 1
            else:
                title, con = firstf_process(i)
                self.bookpages.append(RPage(pnum, title, con))
                pnum += 1

    def gen_book(self):
        print('生成文件...')
        self.book = epub.EpubBook()
        self.book.set_identifier(self.authorid)
        self.book.set_title(self.title)
        self.book.set_language('zh')
        self.book.add_author("TYTY's Python LightNovel Epub Maker")
        css2 = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=css.make_css())
        self.book.add_item(css2)
        self.bookpagelist = [epub.EpubHtml(title=i.t, file_name=str(i.n) + '.xhtml', content=i.c, lang='zh_cn') for i in self.bookpages]
        for i in self.bookpagelist:
            i.add_link(href='style/nav.css', rel='stylesheet', type='text/css')
            self.book.add_item(i)
        self.toc = [epub.Link('1.xhtml', self.bookpagelist[0].title, '1')]
        intoc = [epub.Link(i.file_name, i.title, i.file_name.replace('.xhtml', '')) for i in self.bookpagelist[1:]]
        self.toc.append((epub.Section('章节列表'), tuple(intoc)))
        self.book.toc = tuple(self.toc)
        self.book.add_item(epub.EpubNcx())
        self.book.add_item(epub.EpubNav())
        self.book.spine = ['nav'] + self.bookpagelist
        self.filename = goodtitle(self.title + '.epub')
        epub.write_epub(self.filename, self.book, {})

    def add_pic(self):
        self.picl = picl
        piclist = picl.down_picture()
        self.epubzip = zipfile.ZipFile(self.filename, 'a')
        self.epubcontent = self.epubzip.read('EPUB/content.opf')
        linelist = []
        for i in range(len(piclist)):
            picname = piclist[i][0]
            picformat = picname.split('.')[-1]
            if picformat not in 'jpgjpegpnggifwebpbmp':
                picformat = 'jpeg'
                picname = piclist[i][0] + '.jpg'
            elif picformat == 'jpg':
                picformat = 'jpeg'
            self.epubzip.writestr('EPUB/images/' + picname, piclist[i][1])
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
#    page.get_info()
#    page.get_all()
#    page.get_posts()
#    page.find_picture()
#    page.get_picture()
#    page.gen_page()
#    page.gen_book()
#    page.correct_content()
    print('完成')
