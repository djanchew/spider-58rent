import re
from urllib import request
from lxml import etree

from . import sipder_help


class Spider:

    def __init__(self, url_list):
        self.url_list = url_list

    def __fetch_content(self):
        for city, url in self.url_list:
            print(url)
            try:
                r = request.urlopen(url)
                html = r.read()  # 这里保存的是字节流文件
                html = str(html, encoding='UTF-8')  # 全部转换成字符串
                # print(html)
                self.xp(city, html)
                print('---success---')
            except:
                print('---error---')
                pass

    def xp(self, city, html):
        # 获取font-face，用于数字反爬解码
        pattern = ";base64,([\s\S]*?)'"
        font_face = re.findall(pattern, html)  # html string

        html = etree.HTML(html)  # 可以被xpath的对象

        titles = html.xpath('//ul/li/div[2]/h2/a/text()')
        rooms = html.xpath('//ul/li/div[2]/p[1]/text()')
        price = html.xpath('//ul/li/div[3]/div[2]/b/text()')
        location = html.xpath('//ul/li/div[2]/p[2]/a/text()')
        subway = html.xpath('//ul/li/div[2]/p[2]/text()')

        img_srcs = html.xpath('/html/body/div[4]/div/div[5]/div[2]/ul/li/div[1]/a/img/@lazy_src')
        # print(img_srcs)

        lf = sipder_help.ListRefine(titles, rooms, price, location, subway, font_face[0])
        titles, rooms, price, loc = lf.get_lists()  # 由上，经过去空格、解码处理，获得各个字段的列表（这里似乎存在信息错位）
        sipder_help.save_data(city, titles, rooms, price, loc, img_srcs)  # 存入数据库，并保存img文件

    # 将html保存到本地，作为访问测试用例（其实是网络不太好）
    def local_file(self):
        with open(r'C:\Users\98115\Desktop\text.html', 'rb') as f:
            data = f.read()
            return data

    def run(self):
        self.__fetch_content()


if __name__ == "__main__":
    spider = Spider(sipder_help.get_url_list())
    spider.run()

    # # 本地测试
    # data = spider.local_file()
    # spider.xp('test', data)
