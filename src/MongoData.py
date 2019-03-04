import pymongo
from pymongo import MongoClient
import re
import json


def get_movie_info_collection():
    client = MongoClient()
    db = client.movie_recommender
    movie_info = db.movies
    return movie_info


def get_celeb_info_collection():
    client = MongoClient()
    db = client.movie_recommender
    celebrity_info = db.celebrities_info
    return celebrity_info

def get_error_collection():
    client = MongoClient()
    db = client.movie_recommender
    error_log = db.error_log
    return error_log


def get_arr_item_set(name):
    movie_info = get_movie_info_collection()
    item_set = set()
    for item in movie_info.find():
        item_list = item[name]
        for _item in item_list:
            item_set.add(_item)
    item_set.remove('')
    return item_set


def get_item_set_movie(name):
    movie_info = get_movie_info_collection()
    item_set = set()
    for item in movie_info.find():
        item_set.add(item[name])
    return item_set


def get_item_set_celebrity(name):
    movie_info = get_celeb_info_collection()
    item_set = set()
    for item in movie_info.find():
        item_set.add(item[name])
    return item_set


def print_movie_info(item):
    print('\nTitle:', item['Title'])
    print('Year:', str(item['Year']), '\t', 'Length:', str(item['Length'])+'min')
    print('Nation(s):', '/'.join(item['Nation']))
    print('Rating:', str(item['Rating']))
    print('Voting Number:', str(item['VotingNum']))
    print('Director(s):', '/'.join(item['Directors']))
    print('Starring:', '/'.join(item['Starring']))
    print('Genres:', '|'.join(item['Genres']))
    print('Tags:', '|'.join(item['Tags']))


def print_celebrity_info(item):

    print('\nName:', item['Name'])
    print('Sex:', item['Sex'])
    print('BirthDate:', item['BirthDate'])
    print('BirthPlace:', item['BirthPlace'])
    print('Occupation:', item['Occupation'])
    print('Summary:', item['Summary'])
    print('PicUrl:', item['PicUrl'])
    print('Url', item['Url'])
    print('DirectedMovies:', item['DirectedMovies'])
    print('DirectedUrls:', item['DirectedUrls'])
    print('StarredMovies:', item['StarredMovies'])
    print('StarredUrls:', item['StarredUrls'])


def movie_search_field(field_name, _item, fuzzy, as_array):
    movie_info = get_movie_info_collection()
    num = 0
    if fuzzy:
        print('Fuzzy Search', field_name, _item, '\n')
        if as_array:
            info_set = get_arr_item_set(field_name)
        else:
            info_set = get_item_set_movie(field_name)
        pattern = re.compile('[\s\S]*?' + _item + '[\s\S]*?')
        print('Match', field_name, ':\n')
        for data in info_set:
            if pattern.match(data):
                print(data)
        for item in movie_info.find({field_name: {'$regex': '[\s\S]*?' + _item + '[\s\S]*?'}}):
            print_movie_info(item)
            num = num + 1
    else:
        print('Exact Search', field_name, _item, '\n')
        for item in movie_info.find({field_name: _item}):
            print_movie_info(item)
            num = num + 1
    print('\nTotal:', num, 'movies.')


def search_numeric_data(field_name, _value, choice):
    select_dict = {'larger': 1, 'smaller': 0}
    query = ['$lt', '$gt']
    select = select_dict[choice]
    num = 0
    print('Movie', choice, 'than', _value, 'in', field_name)
    movie_info = get_movie_info_collection()
    for item in movie_info.find({field_name: {query[select]: _value}}):
        print_movie_info(item)
        num = num + 1
    print('\nTotal:', num, 'movies.')


def celebrity_search_field(field_name, _item, fuzzy, as_array):
    celebrity_info = get_celeb_info_collection()
    num = 0
    if fuzzy:
        print('Fuzzy Search', field_name, _item, '\n')
        if as_array:
            info_set = get_arr_item_set(field_name)
        else:
            info_set = get_item_set_celebrity(field_name)
        pattern = re.compile('[\s\S]*?' + _item + '[\s\S]*?')
        print('Match', field_name, ':\n')
        for data in info_set:
            if pattern.match(data):
                print(data)
        for item in celebrity_info.find({field_name: {'$regex': '[\s\S]*?' + _item + '[\s\S]*?'}}):
            print_celebrity_info(item)
            num = num + 1
    else:
        print('Exact Search', field_name, _item, '\n')
        for item in celebrity_info.find({field_name: _item}):
            print_celebrity_info(item)
            num = num + 1
    print('\nTotal:', num, 'celebrities.')


def get_sizes():
    title_length = 0
    max_title = str()
    summary_length = 0
    max_summary = str()
    url_length = 0
    nation_length = 0
    celeb_length = 0
    genre_tag_length = 0
    celebrity_info = get_celeb_info_collection()
    for item in get_movie_info_collection().find():
        title = item['Title']
        summary = item['Summary']
        url = item['Url']
        if len(title) > title_length:
            title_length = len(title)
            max_title = title
        if len(summary) > summary_length:
            summary_length = len(summary)
            max_summary = summary
        if len(url) > url_length:
            url_length = len(url)
        for nation in item['Nation']:
            if len(nation) > nation_length:
                nation_length = len(nation)
        for genre in item['Genres']:
            if len(genre) > genre_tag_length:
                genre_tag_length = len(genre)
        for tag in item['Tags']:
            if len(tag) > genre_tag_length:
                genre_tag_length = len(tag)
        for director in item['Directors']:
            if len(director) > celeb_length:
                celeb_length = len(director)
        for star in item['Starring']:
            if len(star) > celeb_length:
                celeb_length = len(star)

    print(title_length, summary_length, url_length, nation_length, genre_tag_length, celeb_length)
    print(max_title)
    print(max_summary)


def get_celebrity_times():
    movie_info = get_movie_info_collection()
    director_dict = dict()
    star_dict = dict()
    for item in movie_info.find():
        directors = item['Directors']
        starring = item['Starring']
        for director in directors:
            if director in director_dict:
                director_dict[director] = director_dict[director] + 1
            else:
                director_dict.setdefault(director, 1)
        for star in starring:
            if star in star_dict:
                star_dict[star] = star_dict[star] + 1
            else:
                star_dict.setdefault(star, 1)

    director_dict = sorted(director_dict.items(), key=lambda d: d[1], reverse=True)
    fiveplus_directors = dict()
    for item, key in director_dict:
        if key > 3:
            fiveplus_directors[item] = key

    star_dict = sorted(star_dict.items(), key=lambda d: d[1], reverse=True)
    fiveplus_actors = dict()
    for item, key in star_dict:
        if key > 5:
            fiveplus_actors[item] = key
    #print(json.dumps(director_dict, indent=3, ensure_ascii=False))
    #print(len(director_dict), len(fiveplus_directors))
    print(json.dumps(star_dict, indent=3, ensure_ascii=False))
    print(len(fiveplus_directors), len(fiveplus_actors))


if __name__ == '__main__':
    # celebrity_search_field(field_name='Name', _item='昆汀', fuzzy=True, as_array=False)
    # search_field(field_name='Directors', _item='费里尼', fuzzy=True, as_array=True)
    # search_numeric_data(field_name='Rating', _value=9.1, choice='larger')
    # get_sizes()
    get_celebrity_times()
