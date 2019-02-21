import re
import urllib

from fontTools.ttLib import TTFont
from pymongo import MongoClient
import pinyin


class ListRefine(object):
    def __init__(self, titles, rooms, price, location, subway, font_face):
        self.font_decode(font_face)

        self.title_list = self.list_data_strip(titles)
        self.rooms_list = self.list_data_decode(rooms)
        self.price_list = self.list_data_decode(price)
        self.loc_list = self.add_up_location(self.list_data_strip(location), self.list_data_strip(subway))

    def get_lists(self):
        return self.title_list, self.rooms_list, self.price_list, self.loc_list

    def add_up_location(self, list1, list2):
        l = []
        i = 0
        for m in list2:
            try:
                m = list1[i] + ' ' + list1[i + 1] + ' ' + m
                l.append(m)
                i += 2
            except:
                pass
        return l

    def list_data_decode(self, the_list):
        for index, m in enumerate(the_list):
            the_list[index] = self.decode_string(m)
        the_list = [i for i in the_list if i != '']

        return the_list

    def list_data_strip(self, the_list):
        for index, m in enumerate(the_list):
            m = self.decode_string(m)
            the_list[index] = m.strip()
        the_list = [i for i in the_list if i != '']
        return the_list

    def decode_string(self, data):
        l = ""
        a = ''.join(data.split())
        for i in a:
            try:
                l += str(self.map_dict[i])
            except:
                l += str(i)
        return l

    def font_decode(self, font_face):  # 生成字体映射文件，保存对应关系字典
        import base64
        # font_face = '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'
        b = base64.b64decode(font_face)
        with open(r'C:\Users\98115\Desktop\font_face.ttf', 'wb') as f:
            f.write(b)

        font = TTFont(r'C:\Users\98115\Desktop\font_face.ttf')
        # 读取字体的映射关系

        bestcmap = font['cmap'].getBestCmap()
        # print(bestcmap)
        newmap = dict()
        for key in bestcmap.keys():
            value = int(re.search(r'(\d+)', bestcmap[key]).group(1)) - 1
            key = "\\u" + str(hex(key))[2:]
            key = key.encode('latin-1').decode('unicode-escape')
            newmap[key] = value
        # print(newmap)
        self.map_dict = newmap


def get_url_list():
    db = MongoClient("localhost", 27017).test3.area
    result = db.find({'p_id': {'$gt': 1}})
    result = list(result)
    name_list = []
    for i in result:
        the_word = pinyin.get_initial(i['name'])
        name = ''.join(the_word.split())
        name_list.append((name, i['id']))

    return generate_url_list(name_list)


def generate_url_list(name_list):  # url_pattern = 'https://gz.58.com/chuzu/'
    l = []
    for name, id in name_list:
        url = 'https://' + name + '.58.com/chuzu/'
        l.append((id, url))
    return l


def save_data(city_id, titles, rooms, price, loc, img_srcs):
    db = MongoClient("localhost", 27017).house_rent.house_info
    for index, t in enumerate(titles):
        try:
            db.insert_one({
                "city_id": city_id,
                "owner": 'root',
                "renter": '',
                "is_rent": 0,

                "title": t,
                "room": rooms[index],
                "price": price[index],
                "loc": loc[index],
                "img_name": str(city_id) + '_' + str(index),
            })

        except:
            db.insert_one({
                "city_id": city_id,
                "owner": 'root',
                "renter": '',
                "is_rent": 0,

                "title": t,
                "room": rooms[index],
                "price": price[index],
                "loc": '未知',
                "img_name": str(city_id) + '_' + str(index),
            })
        try:
            urllib.request.urlretrieve("https:" + img_srcs[index],
                                       'C:\\Users\98115\Desktop\img_test\%s.jpg' % (str(city_id) + '_' + str(index)))
        except:
            pass

