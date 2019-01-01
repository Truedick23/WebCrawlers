import requests
from bs4 import BeautifulSoup
from random import choice, uniform
import time
import re
import json
from pymongo import MongoClient
import traceback

myHeaders = ["Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
             "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
             "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
             "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
             "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
             "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
             "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
             "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
             "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
             "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
             "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
             "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
             "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
             "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
             "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
             "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52"]

default_params = {'User-Agent': choice(myHeaders)}

params_dict = {'主要参数': ['触控', '处理器型号', '处理器主频', '核心数/线程', '内存容量', '硬盘容量', '屏幕尺寸', '屏幕分辨率',
                    '显卡类型', '显卡芯片', '显存容量'],
            '基本参数': ['触控', '处理器型号', '处理器主频', '核心数/线程', '内存容量', '硬盘容量', '屏幕尺寸', '屏幕分辨率',
                    '显卡类型', '显卡芯片', '显存容量'],
            '处理器': ['处理器系列', '处理器型号', '处理器主频', '最高睿频', '三级缓存', '总线规格', '核心数/线程', '核心类型',
                    '主板芯片组', '制程工艺', '功耗'],
            '存储设备': ['内存描述', '内存容量', '硬盘描述', '硬盘容量', '光驱类型'],
            '显示屏': ['屏幕尺寸', '屏幕尺寸范围', '屏幕比例', '屏幕分辨率', '屏幕技术'],
            '显卡': ['显卡类型', '显卡芯片', '显存类型', '显存容量', '显存位宽'],
            '多媒体设备': ['摄像头', '音频系统', '扬声器', '麦克风'],
            '网络通信': ['无线网卡', '有线网卡', '蓝牙'],
            'I/O接口': ['数据接口', '视频接口', '音频接口', '其它接口'],
            '输入设备': ['指取设备', '键盘描述'],
            '电源描述': ['电池类型', '续航时间', '电源适配器'],
            '外观特征': ['外壳材质', '外观描述', '外观尺寸', '产品重量'],
            '其它信息': ['其他特点', '包装清单', '可选配件', '附带软件', '售后服务'],
            '推荐适用类型': ['触控', '影音游戏', '家庭娱乐']}


def get_lenovo_info_collection():
    client = MongoClient("localhost", 27017)
    db = client.lenovo
    collection = db.laptop
    return collection


def get_existed_urls():
    lenovo_collection = get_lenovo_info_collection()
    return lenovo_collection.distinct('Url')


def get_html_text(url):
    try:
        r = requests.get(url)
        r.headers = default_params
        r.encoding = 'gbk'
        r.raise_for_status()
        return r.text
    # ['HTTPError', 'AttributeError', 'TypeError', 'InvalidIMDB']
    except AttributeError:
        print('\n', url, 'Attribute Error!\n')
        return ''

    except requests.exceptions.HTTPError:
        print('\n', url, 'HTTP Error!\n')
        return ''

    except requests.exceptions.ConnectionError:
        print('Check if Internet is connected.')
        return


def scratch_nav_pages(url):
    # filter = ['小米笔记本Air', '荣耀MagicBook', 'MateBook XPro', '戴尔燃7000']
    url_set = set()
    text = get_html_text(url)
    soup = BeautifulSoup(text, 'html.parser')
    match = re.findall(r'<a href="http://product.yesky.com/product/[0-9]*/[0-9]*/" target="_blank">([\s\S]*?)</a>',
                       text)
    for i in match:
        if i[0] == '<':
            match.remove(i)

    match = match[0:-4]
    print(match)

    for title in match:
        for i in soup.find_all(name='a', attrs={'target': '_blank'}):
            if i.string == title:
                print(i['href'])
                url_set.add(i['href'])
    return url_set


def crawl_detailed_data(url):
    text = get_html_text(url)
    soup = BeautifulSoup(text, 'html.parser')
    info_dict = dict()
    for key in params_dict:
        info_dict.setdefault(key, dict())

    for i in soup.find_all(name='table', attrs={'class': 'paramtable-b'}):

        for field in i.contents:
            result = re.findall('<th>([\s\S]*?)</th>\n<td>([\s\S]*?)</td>', str(field))
            # if result[0] == '<' or result[1][0] == '<' or result[0][0] == '\\' or result[0][0] == '\\':
            #     pass
            for item in result:
                match1 = re.findall('target="_blank">([\s\S]*?)</a>', item[0])
                match2 = re.findall('target="_blank">([\s\S]*?)</a>', item[1])
                if len(match1) != 0:
                    field1 = match1[0]
                else:
                    field1 = item[0]
                if len(match2) != 0:
                    field2 = match2[0]
                else:
                    field2 = item[1]
                field1 = field1.lstrip()
                field2 = field2.lstrip()
                for key in params_dict:
                    for item in params_dict[key]:
                        if item == field1:
                            # print(key, field1, field2)
                            info_dict[key].setdefault(field1, field2)
                if len(field1) == 0 or len(field2) == 0:
                    pass
    return info_dict


def crawl_pic_set(url):
    pic_set = set()
    pic_dict = list()
    text = get_html_text(url)
    soup = BeautifulSoup(text, 'html.parser')
    for pic_ul in soup.find_all(name='img', attrs={'onerror': 'imageNotExsit(120, this);'}):
        pic_url = pic_ul['src']
        size = re.findall(r'http://dynamic-image.yesky.com/(\S*?)x(\S*?)/resources/product/[0-9]*/[\s\S]*?', pic_url)
        width = int(size[0][0])
        height = int(size[0][1])
        match = re.findall(r'([\s\S]*?)--点击可看清晰大图', pic_ul['title'])
        title = match[0]
        if pic_url not in pic_set:
            pic_set.add(pic_url)
            pic_dict.append({'Url': pic_url, 'Title': title, 'Width': width, 'Height': height})
    return pic_dict


def crawl_policy(url):
    text = get_html_text(url)
    soup = BeautifulSoup(text, 'html.parser')
    policy_str = str()
    policy = soup.find(name='table', attrs={'class': 'brand-aftersaleinfo'})
    for item in policy.contents:
        match = re.findall(r'<td>([\s\S]*?)</td>', str(item))
        if len(match) != 0:
            policy_str = policy_str + match[0] + '\n'
    return policy_str


def crawl_computer(url):
    text = get_html_text(url)
    soup = BeautifulSoup(text, 'html.parser')
    print(url)
    try:
        title = soup.find(name='h1').string
        print(title)

        price = float(soup.find(name='dl', attrs={'class': 'gbckjg'}).dt.strong.string[2:])
        print(price)

        mrminpic_url = soup.find(name='div', attrs={'class': 'gbzcpt', 'id': 'mrminpic'}).a.img['src']
        print(mrminpic_url)

        data = soup.find(name='ul', attrs={'class': 'tvmaincx'})
        data_list_simple = dict()
        for i in data.contents:
            data_find = re.findall('<em>([\s\S]*?)</em><span>([\s\S]*?)</span></li>', str(i))
            if len(data_find) != 0:
                field1 = data_find[0][0]
                field2 = data_find[0][1]
                data_list_simple.setdefault(field1, field2)
        print(json.dumps(data_list_simple, indent=3, ensure_ascii=False))

        params_dict = crawl_detailed_data(url + 'param.shtml')
        print(json.dumps(params_dict, indent=3, ensure_ascii=False))

        pic_dict = crawl_pic_set(url + 'pic.shtml')
        print(json.dumps(pic_dict, indent=3, ensure_ascii=False))

        policy = crawl_policy(url + 'maintain.shtml')
        print(policy)

    except:
        print('Error occured')
        lenovo_info = get_lenovo_info_collection()

        lenovo_info.insert_one({
            'Url': url,
            'Info': 'Error'
        })
        return

    lenovo_info = get_lenovo_info_collection()

    lenovo_info.insert_one({
        'Url': url,
        'Title': title,
        'Price': price,
        'MainPic': mrminpic_url,
        'Pics': pic_dict,
        'BasicData': data_list_simple,
        'DetailedData': params_dict,
        'Policy': policy
    })

def update_data():
    lenovo_info = get_lenovo_info_collection()
    for url in get_existed_urls():
        item = lenovo_info.find_one({'Url': url})
        try:
            basic_dict = item['BasicData']
            memory = re.findall(r'^([0-9]*)G', basic_dict['内存容量'])[0]
            print(memory)
            basic_dict['内存容量'] = memory + 'GB'
            lenovo_info.update_one(
                {'Url': url},
                {'$set': {'BasicData': basic_dict}}
            )
        except:
            print(traceback.format_exc())


def get_basic_info():
    data_dict = dict()
    data_frequency_dict = dict()
    keys = ['核心数/线程', '屏幕尺寸', '屏幕分辨率', '显卡类型', '内存容量', '处理器型号',
            '显存容量', '硬盘容量', '处理器主频', '显卡芯片', '触控', '指纹识别']
    for key in keys:
        data_dict.setdefault(key, list())
    lenovo_info = get_lenovo_info_collection()
    urls = get_existed_urls()
    for url in urls:
        info = lenovo_info.find_one({'Url': url})['BasicData']
        for key in info:
            try:
                if info[key] not in data_dict[key]:
                    data_dict[key].append(info[key])
            except:
                print(traceback.format_exc())
                print(key, url)
    print(json.dumps(data_dict, indent=2, ensure_ascii=False, sort_keys=True))
    '''
    for data in data_dict['内存容量']:
        match = re.findall(r'^([0-9]*)G', data)
        print(match, data)
    '''

    for key in keys:
        sub_dict = dict()
        for value in data_dict[key]:
            sub_dict.setdefault(value, 0)
        data_frequency_dict.setdefault(key, sub_dict)
    for url in urls:
        info = lenovo_info.find_one({'Url': url})['BasicData']
        for key in info:
            try:
                data_frequency_dict[key][info[key]] = data_frequency_dict[key][info[key]] + 1
            except:
                print(traceback.format_exc())
                print(key, url)
    # print(json.dumps(data_frequency_dict, indent=2, ensure_ascii=False, sort_keys=True))



def delete_error():
    lenovo_info = get_lenovo_info_collection()
    lenovo_info.update_many(
        {'内存容量': {'$exists': True}},
        {'$unset': {'内存容量': ''}}
    )



def process():
    for page_num in range(1, 61):
        url_set = scratch_nav_pages('http://product.yesky.com/notebookpc/lenovo/list' + str(page_num) + '.html')
        i = 0
        for url in url_set:
            i = i + 1
            if url not in get_existed_urls():
                time.sleep(uniform(0.4, 0.7))
                crawl_computer(url)
                print('Progress: \n Page {} of {}, Item {} of {}'.format(page_num, 61, i, len(url_set)))


def download_pic():
    from urllib.parse import urlsplit
    lenovo = get_lenovo_info_collection()
    num = len(get_existed_urls())
    i = 0
    for url in lenovo.distinct('MainPicUrl'):
        time.sleep(0.22)
        i = i + 1
        pic_name = urlsplit(url).path.split('/')[-1]
        path = 'F:/lenovo/' + pic_name
        html = requests.get(url)
        with open(path, 'wb') as file:
            file.write(html.content)
        lenovo.update_many(
            {'MainPicUrl': url},
            {'$set': {'PicName': pic_name}}
        )
        print(pic_name)
        print('Progress: {:.2%}'.format(i / num))


if __name__ == '__main__':
    # process()
    # crawl_computer('http://product.yesky.com/product/1050/1050230/')
    # crawl_detailed_data('http://product.yesky.com/product/1053/1053889/param.shtml')
    # crawl_pic_set('http://product.yesky.com/product/1050/1050230/pic.shtml')
    # crawl_policy('http://product.yesky.com/product/1050/1050230/maintain.shtml')
    # de_comma()
    # delete_error()
    get_basic_info()
    # download_pic()
    # update_data()