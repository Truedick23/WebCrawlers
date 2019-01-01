import requests
from bs4 import BeautifulSoup
from random import choice
import re
import json
from pymongo import MongoClient

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

def get_html_text(url):
    try:
        r = requests.get(url)
        r.headers = default_params
        r.encoding = 'utf-8'
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


def get_js(url, param):
    try:
        r = requests.post(url)
        r.headers = default_params
        r.encoding = 'utf-8'
        r.raise_for_status()
        json_response = r.content.decode()
        dist_json = json.loads(json_response)
        return(type(dist_json))
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


def get_lenovo_info_collection():
    client = MongoClient()
    db = client.lenovo
    collection = db.laptop
    return collection


def get_existed_titles():
    lenovo_collection = get_lenovo_info_collection()
    return lenovo_collection.distinct('Title')


def get_laptop_pages():
    text = get_html_text('https://shop.lenovo.com.cn/juhe/page_1.html')
    soup = BeautifulSoup(text, 'html.parser')
    laptop_list = list()
    # item = soup.find(name='ul', attrs={'id': 'productList', 'class': 'clearfix'})
    for item in soup.find_all(name='a', attrs={'target': '_blank'}):
        if 'lenovo.com.cn/product/' in item['href']:
            print(item['href'])
            laptop_list.append(item['href'])
    result = re.findall(r'http://item.lenovo.com.cn/product/([\s\S]*?).html', text)
    return laptop_list


def get_price(url):
    param = [{"uri":"/batch/openapi/goods/detail/mget/B00001","param":{"code":1002023,"ss":709}},{"uri":"/batch/promoapi/api/front/getPromoMsg.jhtm","param":{"gcode":1002023,"terminal":1,"shopId":1, "ss":709}}]
    js = get_js(url, param=param)
    print(js.find('6999'))



def process(url):

    data_dict = dict()
    text = get_html_text(url)
    soup = BeautifulSoup(text, 'html.parser')
    info_dict = dict()
    picUrls = list()

    try:
        item  = soup.find(name='h1', attrs={'class': 'title', 'id': 'span_product_name'})
        item_title = item['title']
        if item_title in get_existed_titles():
            return
    except Exception:
        print('Error getting title!')
        return

    try:
        item = soup.find(name='span', attrs={'class': 'good_code'})
        code = item.span.string
    except Exception:
        print('Error getting code!')
        return

    try:
        item  = soup.find(name='div', attrs={'class': 'operate_money'})
        print(item.contents)
    except Exception:
        print('Error getting price!')
        return

    try:
        pic = soup.find(name='img', attrs={'id':'winpic', 'class':'pic'})
        mainpicUrl = pic['src'][2:]
    except Exception:
        print('Error getting main pic!')
        return

    try:
        for item in soup.find_all(name='img', attrs={'class':'lazy lazy_img', 'title':'', 'alt':''}):
            picUrls.append(item['data-original'][2:])
    except Exception:
        print('Error getting other pic!')
        return

    '''
    try:
        for item in soup.find_all(name='div', attrs={'class': 'assess_item'}):
            print(item.div['class'])
        users = re.findall(r'<div class="assess_name">([\s\S]*?)</div>', text)
        time = re.findall(r'<div class="assess_time"([\s\S]*?)</div>', text)
        comment_text = re.findall(r'<div class="assess_con"([\s\S]*?)</div>', text)
        print(users)
        print(time)
        print(comment_text)
    except Exception:
        print('Error getting comments!')
        '''

    try:
        for item in soup.find_all(name='div', attrs={'class': 'good_item'}):
            title = item.div.div.string
            if '\t' in title:
                title = title[0:-1]
            content = [str(i) for i in item.contents][0:-2]
            #print(content)
            sub_dict = dict()
            for field in content:
                try:
                    match1 = re.findall(r'<div class="col_one">([\s\S]*?)</div>', field)
                    match2 = re.findall(r'<div class="col_one col_values col_two1">([\s\S]*?)</div>', field)
                    key = match1[0]
                    value = match2[0]
                    if key == '' or value == '':
                        pass
                    if key == 'USB3.0':
                        key = 'USB30'
                    elif key == 'USB2.0':
                        key = 'USB20'
                    sub_dict.setdefault(key, value)
                except Exception:
                    pass
            info_dict.setdefault(title, sub_dict)
    except Exception:
        print('Error getting detailed!')
    if not info_dict:
        return

    print('Title:', item_title)
    print('Code:', code)
    print('Main Pic:', mainpicUrl)
    print('Other Pics:', picUrls)
    print('Data:')
    print(json.dumps(info_dict, indent=3, ensure_ascii=False))

    lenovo = get_lenovo_info_collection()
    '''lenovo.insert_one({
        'Title': item_title,
        'Code': code,
        'Price': price,
        'MainPic': mainpicUrl,
        'OtherPics': picUrls,
        'Data': data_dict
    })'''

        # data_dict.setdefault(title, dict())
    # print('\n')


    '''
    field_set = list()
    for field in re.findall(r'<div class="item_title">([\s\S]*?)</div>', text):
        field_set.append(field)
    reg_list = ['<div class="good_item">([\s\S]*?)<div class="item_row item-row-last"']
    '''

def download_pics():
    lenovo = get_lenovo_info_collection()
    for url in lenovo.distinct('MainPic'):


if __name__ == '__main__':
    laptops = get_laptop_pages()
    for laptop in laptops:
        process(laptop)
    # get_price('https://papi.lenovo.com.cn/cache/query?m=hget&k=personal_init_1001895&f=A%E9%9D%A2&ss=903&callback=jQuery18309043927043199611_1544505811174&_=1544505814903')