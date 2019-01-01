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


def get_celeb_info_collection():
    client = MongoClient()
    db = client.movie_recommender
    celebrity_info = db.celebrities_info
    return celebrity_info


def get_celeb_exists_list():
    celebrity_info = get_celeb_info_collection()
    celeb_lists = celebrity_info.distinct('Url')
    return celeb_lists


def get_unprocessed_movie_url():
    movie_info = get_movie_info_collection()
    url_list = set()
    for item in movie_info.find({'DirectorUrls': {"$exists": False}}):
        url_list.add((item['Title'], item['Url']))
    return url_list


def get_total_number():
    movie_info = get_movie_info_collection()
    movie_set = set()
    for item in movie_info.find():
        movie_set.add(item)
    return len(movie_set)


def scratch_movie_celebs(url, title):
    print(url)
    text = get_html_text(url)
    soup = BeautifulSoup(text, 'html.parser')
    movie_info = get_movie_info_collection()
    starring_set = list()
    director_set = list()
    try:
        for item in soup.find_all(name='a', attrs={'rel': 'v:directedBy'}):
            _url = 'https://movie.douban.com' + item['href']
            director_set.append(_url)
        for item in soup.find_all(name='a', attrs={'rel': 'v:starring'}):
            _url = 'https://movie.douban.com' + item['href']
            starring_set.append(_url)
    except AttributeError:
        print('Attribute Error!')
    except TypeError:
        print('Type Error!')

    print('\nDirector(s): \n')
    len_directors = len(director_set)
    for index in range(len_directors):
        director_url = director_set[index]
        print('{} of {}'.format(index+1, len_directors))
        flag = True
        if director_url not in get_celeb_exists_list():
            print(director_url)
            time.sleep(uniform(0.1, 0.4))
            flag = scratch_celebrity_info(director_url)
        time.sleep(uniform(0.4, 0.6))
        if flag:
            add_title_and_role_to_celebrity(director_url, url, title, 'director')

    len_stars = len(starring_set)
    print('\nStarring(s): \n')
    for index in range(len_stars):
        starring_url = starring_set[index]
        print('{} of {}'.format(index+1, len_stars))
        flag = True
        if starring_url not in get_celeb_exists_list():
            print(starring_url)
            time.sleep(uniform(0.2, 0.5))
            flag = scratch_celebrity_info(starring_url)
        time.sleep(uniform(0.3, 0.6))
        if flag:
            add_title_and_role_to_celebrity(starring_url, url, title, 'starring')

    movie_info.update_one(
        {'Url': url},
        {'$set': {'DirectorsUrls': director_set, 'StarringUrls': starring_set}})


def add_title_and_role_to_celebrity(url, movie_url, title, role):
    item_role_dict = {'director': 'DirectedMovies', 'starring': 'StarredMovies'}
    item_urls_dict = {'director': 'DirectedUrls', 'starring': 'StarredUrls'}
    celebrity_info = get_celeb_info_collection()
    fields = celebrity_info.find_one({'Url': url})
    print('Celebrity', fields['Name'], 'added')
    print('Title:', title, 'Role:', role, '\n')
    celebrity_info.update_one(
        {'Url': url},
        {'$addToSet': {item_role_dict[role]: title, item_urls_dict[role]: movie_url}}
    )
    print('Updated')


def unset_fields():
    celebrity_info = get_movie_info_collection()
    for (title, url) in get_updated_celeb_movie_url():
        print(url)
        celebrity_info.update_one(
            {'Url': url},
            {'$unset': {'DirectorsUrls': '', 'StarringUrls': ''}}
        )
    print('Unset finished!')

def scratch_celebrity_info(url):
    if url in get_celeb_exists_list():
        print('Skip!')
        return

    text = get_html_text(url)
    soup = BeautifulSoup(text, 'html.parser')
    try:
        Name = soup.find(name='h1').string
    except AttributeError:
        print('Attribute Error!', url)
        return False
    tags_list = list()
    info_list = list()
    Summary = str()
    PicUrl = str()
    tags_dict = {'性别': 'Sex', '出生日期': 'BirthDate', '出生地': 'BirthPlace', '职业': 'Occupation'}
    try:
        for item in soup.find(name='div', attrs={'class': 'info'}).ul.children:
            for field in re.findall(r'<span>([\s\S]*?)</span>', str(item)):
                if len(field) > 0:
                    tags_list.append(field)
            for field in re.findall(r'</span>: \n\s+([\s\S]*?)\n\s+</li>', str(item)):
                if len(field) > 0:
                    info_list.append(field)
    except Exception:
        print('Info Finding Error!')

    try:
        for item in soup.find_all(name='span', attrs={'class': "all hidden"}):
            str_list = item.contents
            # print(str_list)
            for _str in str_list:
                # print(_str)
                try:
                    matched = re.findall(r'\u3000\u3000([\s\S]*?)$', _str)
                    # print(matched)
                    Summary += matched[0]
                except TypeError:
                    pass
                except IndexError:
                    pass
        if Summary == '':
            for item in soup.find_all(name='div', attrs={'class': 'bd'}):
                str_list = item.contents
                for _str in str_list:
                    try:
                        matched = re.findall(r'\u3000\u3000([\s\S]*?)\n', _str)
                        Summary += matched[0]
                    except TypeError:
                        pass
                    except IndexError:
                        pass
    except Exception:
        print('Summary Error!')

    try:
        PicUrl = soup.find(name='img', attrs={'title': '点击看大图'})['src']
    except Exception:
        PicUrl = 'https://img3.doubanio.com/f/movie/8dd0c794499fe925ae2ae89ee30cd225750457b4/pics/movie/celebrity-default-medium.png'
        print('Pic Error!')

    Sex = str()
    BirthDate = str()
    BirthPlace = str()
    Occupations = list()
    DirectedMovies = list()
    DirectedUrls = list()
    StarredMovies = list()
    StarredUrls = list()
    for index in range(min(len(tags_list), len(info_list))):
        tag = tags_list[index]

        if tag in tags_dict:
            tag = tags_dict[tags_list[index]]
            info = info_list[index]
            if tag == 'Sex':
                Sex = info
            if tag == 'BirthDate':
                BirthDate = info
            if tag == 'BirthPlace':
                BirthPlace = info
            if tag == 'Occupation':
                Occupations = info_list[index].split(' / ')

    print('\nName:', Name)
    print('Sex:', Sex)
    print('BirthDate:', BirthDate)
    print('BirthPlace:', BirthPlace)
    print('Occupation:', Occupations)
    print('Summary:', Summary)
    print('PicUrl:', PicUrl)
    print('Url', url)
    print('DirectedMovies:', DirectedMovies)
    print('DirectedUrls:', DirectedUrls)
    print('StarredMovies:', StarredMovies)
    print('StarredUrls:', StarredUrls)

    celebrity_info = get_celeb_info_collection()
    celebrity_info.insert_one({
        'Name': Name,
        'Sex': Sex,
        'BirthDate': BirthDate,
        'BirthPlace': BirthPlace,
        'Occupation': Occupations,
        'Summary': Summary,
        'PicUrl': PicUrl,
        'Url':  url,
        'DirectedMovies': DirectedMovies,
        'DirectedUrls': DirectedUrls,
        'StarredMovies': StarredMovies,
        'StarredUrls': StarredUrls
    })
    print('Inserted Celebrity Info')
    return True


def get_not_updated_celeb_movie_url():
    movie_info = get_movie_info_collection()
    url_list = set()
    for item in movie_info.find({'$or': [{'DirectorsUrls': {"$exists": False}}, {'StarringUrls': {"$exists": False}}]}):
        url_list.add((item['Title'], item['Url']))
    return url_list


def get_updated_celeb_movie_url():
    movie_info = get_movie_info_collection()
    url_list = set()
    for item in movie_info.find({'$and': [{'DirectorsUrls': {"$exists": True}}, {'StarringUrls': {"$exists": True}}]}):
        url_list.add((item['Title'], item['Url']))
    return url_list


def add_celeb_url_to_movie_collection():
    num = 0
    for field in get_not_updated_celeb_movie_url():
        num = num + 1
        time.sleep(uniform(0.2, 0.5))
        print(field[0])
        scratch_movie_celebs(field[1], field[0])
        print('\nProgress: {:.2%}\n'
              .format(len(get_updated_celeb_movie_url()) /
                      (len(get_not_updated_celeb_movie_url()) + len(get_updated_celeb_movie_url()))))


def process():
    # ignite_scratching()
    add_celeb_url_to_movie_collection()

if __name__ == '__main__':
    # scratch_movie_celebs('https://movie.douban.com/subject/26588308/')
    # scratch_celebrity_info('https://movie.douban.com/celebrity/1054443/')
    process()
    # scratch_movie_celebs('https://movie.douban.com/subject/1291832/', '低俗小说 Pulp Fiction')
    # scratch_movie_celebs('https://movie.douban.com/subject/6307447/', '被解救的姜戈 Django Unchained')
    # unset_fields()
    # print(len(get_updated_celeb_movie_url()))
    # print(get_celeb_exists_list())