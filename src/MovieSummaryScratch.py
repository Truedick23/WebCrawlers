import requests
from bs4 import BeautifulSoup
from random import choice, uniform
import pymongo
import re
import time
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

params = {'User-Agent': choice(myHeaders)}


def get_html_text(url):
    try:
        r = requests.get(url)
        r.headers = params
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


def get_movie_info_collection():
    client = MongoClient()
    db = client.movie_recommender
    movie_info = db.movies_info
    return movie_info


def get_not_updated_summary_movie_url():
    movie_info = get_movie_info_collection()
    url_list = set()
    for item in movie_info.find({'Summary': {"$exists": False}}):
        url_list.add((item['Url'], item['Title']))
    return url_list


def get_updated_summary_movie_url():
    movie_info = get_movie_info_collection()
    url_list = set()
    for item in movie_info.find({'Summary': {"$exists": True}}):
        url_list.add(item['Url'])
    return url_list


def get_null_summary_movie_url():
    movie_info = get_movie_info_collection()
    url_list = set()
    for item in movie_info.find({'summary': 'NULL'}):
        url_list.add(item['Url'])
    return url_list


def get_summary_movie_url():
    movie_info = get_movie_info_collection()
    url_list = set()
    for item in movie_info.find({'summary': {'$ne': 'NULL'}}):
        url_list.add(item['Url'])


def get_movie_summary(url):
    text = get_html_text(url)
    soup = BeautifulSoup(text, 'html.parser')
    movie_info = get_movie_info_collection()
    summary = str()
    for item in soup.find_all(name='span', attrs={'class': "", 'property': "v:summary"}):
        str_list = item.contents
        for _str in str_list:
            # print(_str)
            try:
                matched = re.findall(r'\u3000\u3000([\s\S]*?)\n', _str)
                summary += matched[0]
            except TypeError:
                pass
            except IndexError:
                pass
    movie_info.update_one({'Url': url}, {'$set': {'Summary': summary}})
    print(summary, '\nUpdated\n')


def process():
    num = 0
    for url, title in get_not_updated_summary_movie_url():
        num = num + 1
        time.sleep(uniform(0.5, 1.0))
        print(title)
        get_movie_summary(url)
        if num % 5 == 0:
            print('\nProgress: {:.2%}\n'
                  .format(len(get_updated_summary_movie_url()) /
                          (len(get_not_updated_summary_movie_url()) + len(get_updated_summary_movie_url()))))


if __name__ == '__main__':
    process()
    get_movie_summary('https://movie.douban.com/subject/1292553/?from=subject-page')
    # print(get_updated_summary_movie_url())

