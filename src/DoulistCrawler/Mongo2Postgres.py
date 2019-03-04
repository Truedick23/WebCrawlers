import psycopg2
import pymongo
from pymongo import MongoClient

def get_movie_info_collection():
    client = MongoClient()
    db = client.felkub
    movie_info = db.movies
    return movie_info

def get_directors_info_collection():
    client = MongoClient()
    db = client.felkub
    movie_info = db.directors
    return movie_info

def get_starring_info_collection():
    client = MongoClient()
    db = client.felkub
    movie_info = db.starring
    return movie_info

def get_genres_info_collection():
    client = MongoClient()
    db = client.felkub
    movie_info = db.genres
    return movie_info

def create_movies_table():
    conn = psycopg2.connect(dbname="movies_recommender", user="lenovo", password="josephlive199823")
    cursor = conn.cursor()
    create_sql = '''create table movies(
          id serial,
          title varchar(500) not null ,
          url varchar(100) not null ,
          year integer not null ,
          rating float not null ,
          votes integer not null ,
          length integer not null ,
          imdb integer not null ,
          picname varchar(100) not null ,
          nation varchar(100)[] not null ,
          genres varchar(100)[] not null ,
          tags varchar(100)[] not null ,
          directors varchar(100)[] not null ,
          starring varchar(100)[] not null ,
          summary varchar(1000) not null 
        )'''
    cursor.execute(create_sql)
    conn.commit()
    conn.close()

def create_starring_table():
    conn = psycopg2.connect(dbname="movies_recommender", user="lenovo", password="josephlive199823")
    cursor = conn.cursor()
    create_sql = '''create table starring(
          id serial,
          fullname varchar(500) not null ,
          shortname varchar(200) not null ,
          url varchar(300) not null ,
          birthdate varchar(100) not null ,
          birthplace varchar(100) not null ,
          occupation text[] not null ,
          picname varchar(500) not null ,
          starringnum integer not null ,
          starredurls text[] not null ,
          starredtitles text[] not null ,
          summary text not null ,
          averagerating float not null ,
          averagevotes float not null 
    )
    '''
    cursor.execute(create_sql)
    conn.commit()
    conn.close()

def create_directors_table():
    conn = psycopg2.connect(dbname="movies_recommender", user="lenovo", password="josephlive199823")
    cursor = conn.cursor()
    create_sql = '''create table directors(
          id serial,
          fullname varchar(500) not null ,
          shortname varchar(200) not null ,
          url varchar(300) not null ,
          birthdate varchar(100) not null ,
          birthplace varchar(100) not null ,
          occupation text[] not null ,
          picname varchar(500) not null ,
          directnum integer not null ,
          directedurls text[] not null ,
          directedtitles text[] not null ,
          summary text not null ,
          averagerating float not null ,
          averagevotes float not null 
        )'''
    cursor.execute(create_sql)
    conn.commit()
    conn.close()

def create_genres_table():
    conn = psycopg2.connect(dbname="movies_recommender", user="lenovo", password="josephlive199823")
    cursor = conn.cursor()
    create_sql = '''create table genres(
              id serial primary key ,
              name varchar(100) not null ,
              times integer not null ,
              movietitles text[],
              movieurls text[]
            )'''
    cursor.execute(create_sql)
    conn.commit()
    conn.close()

def insert_movie(item):
    title = "'" + item['Title'].replace("'", "''") + "'"
    url = "'" + item['Url'] + "'"
    year = str(item['Year'])
    rating = str(item['Rating'])
    votes = str(item['VotingNum'])
    length = str(item['Length'])
    imdb = str(item['IMDB'])
    picname = "'" + item['PicName'] + "'"

    nation = item['Nation']
    nation_str = "\'{\"" + '\",\"'.join(nation).replace("'", "''") + "\"}\'"

    genres = item['Genres']
    genres_str = "\'{\"" + '\",\"'.join(genres).replace("'", "''") + "\"}\'"

    tags = item['Tags']
    for tag in tags:
        if '"' in tag:
            tags.remove(tag)

    tags_str = "\'{\"" + '\",\"'.join(tags).replace("'", "''") + "\"}\'"

    directors = item['Directors']
    directors_str = "\'{\"" + '\",\"'.join(directors).replace("'", "''") + "\"}\'"

    starring = item['Starring']
    for star in starring:
        if '"' in star:
            starring.remove(star)
    starring_str = "\'{\"" + '\",\"'.join(starring).replace("'", "''") + "\"}\'"

    summary = "'" + item['Summary'].replace("'", "''") + "'"

    insert_sql = "insert into movies" + "(title, url, year, rating, votes, length, imdb, picname, nation, genres, tags, directors, starring, summary) values(" \
    + title + ',' + url + ',' + year + ',' + rating + ',' + votes + ',' + length + ',' + imdb + ',' + picname +\
    ',' + nation_str + ',' + genres_str + ',' + tags_str + ',' + directors_str + ',' + starring_str + ',' + summary + ')'

    conn = psycopg2.connect(dbname="movies_recommender", user="lenovo", password="josephlive199823")
    cursor = conn.cursor()
    cursor.execute(insert_sql)
    conn.commit()
    conn.close()

def insert_starring(item):
    fullName = "'" + item['FullName'].replace("'", "''") + "'"
    shortName = "'" + item['ShortName'].replace("'", "''") + "'"
    url = "'" + item['Url'] + "'"
    birthdate = "'" + item['BirthDate'].replace("'", "''") + "'"
    birthplace = "'" + item['BirthPlace'].replace("'", "''") + "'"

    picname = "'" + item['PicName'] + "'"
    star_num = item['StarNum']

    average_rating = item['AverageRating']
    average_votes = item['AverageVotes']

    occupation = item['Occupation']
    occupation_str = "\'{\"" + '\",\"'.join(occupation).replace("'", "''") + "\"}\'"

    starred_urls = item['StarredUrls']
    starred_urls_str = "\'{\"" + '\",\"'.join(starred_urls).replace("'", "''") + "\"}\'"

    starred_titles = item['StarredTitles']
    starred_titles_str = "\'{\"" + '\",\"'.join(starred_titles).replace('"', "'").replace("'", "''") + "\"}\'"

    summary = "'" + item['Summary'].replace("'", "''") + "'"

    insert_sql = "insert into starring" + "(fullname, shortname, url, birthdate, birthplace, occupation, picname, starringnum, starredurls, starredtitles, summary, averagerating, averagevotes) values(" \
                 + fullName + ',' + shortName + ',' + url + ',' + birthdate + ',' + birthplace + ',' + occupation_str + ',' + picname + ',' + str(star_num) \
                 + ',' + starred_urls_str + \
                 ',' + starred_titles_str + ',' + summary + ',' + str(average_rating) + ',' + str(average_votes) + ')'

    conn = psycopg2.connect(dbname="movies_recommender", user="lenovo", password="josephlive199823")
    cursor = conn.cursor()
    cursor.execute(insert_sql)
    conn.commit()
    conn.close()

def insert_genre(item):
    name = "'" + item['Name'].replace("'", "''") + "'"
    times = str(item['Times'])
    movie_titles = "\'{\"" + '\",\"'.join(item['MovieTitles']).replace('"', "'").replace("'", "''") + "\"}\'"
    movie_urls = "\'{\"" + '\",\"'.join(item['MovieUrls']).replace('"', "'").replace("'", "''") + "\"}\'"

    insert_sql = "insert into genres(name, times, movietitles, movieurls) VALUES (" + \
    name + ','+ times + ',' + movie_titles + ',' + movie_urls + ")"

    conn = psycopg2.connect(dbname="movies_recommender", user="lenovo", password="josephlive199823")
    cursor = conn.cursor()
    cursor.execute(insert_sql)
    conn.commit()
    conn.close()

def insert_director(item):
    fullName = "'" + item['FullName'].replace("'", "''") + "'"
    shortName = "'" + item['ShortName'].replace("'", "''") + "'"
    url = "'" + item['Url'] + "'"
    birthdate = "'" + item['BirthDate'].replace("'", "''") + "'"
    birthplace = "'" + item['BirthPlace'].replace("'", "''") + "'"

    picname = "'" + item['PicName'] + "'"
    directed_num = item['DirectNum']

    average_rating = item['AverageRating']
    average_votes = item['AverageVotes']

    occupation = item['Occupation']
    occupation_str = "\'{\"" + '\",\"'.join(occupation).replace("'", "''") + "\"}\'"

    directed_urls = item['DirectedUrls']
    directed_urls_str = "\'{\"" + '\",\"'.join(directed_urls).replace("'", "''") + "\"}\'"

    directed_titles = item['DirectedTitles']
    directed_titles_str = "\'{\"" + '\",\"'.join(directed_titles).replace('"', "'").replace("'", "''") + "\"}\'"

    summary = "'" + item['Summary'].replace("'", "''") + "'"

    insert_sql = "insert into directors" + "(fullname, shortname, url, birthdate, birthplace, occupation, picname, directnum, directedurls, directedtitles, summary, averagerating, averagevotes) values(" \
    + fullName + ',' + shortName + ',' + url + ',' + birthdate + ',' + birthplace + ',' + occupation_str + ',' + picname + ',' + str(directed_num) + ',' + directed_urls_str + \
    ',' + directed_titles_str + ',' + summary + ',' + str(average_rating) + ',' + str(average_votes) + ')'

    conn = psycopg2.connect(dbname="movies_recommender", user="lenovo", password="josephlive199823")
    cursor = conn.cursor()
    cursor.execute(insert_sql)
    conn.commit()
    conn.close()

def mongo2postgres():
    mongo = get_starring_info_collection()
    for item in mongo.find({'Transported': {'$exists': False}}):
        name = item['ShortName']
        print(name)
        insert_starring(item)
        mongo.update_one(
            {'_id': item['_id']},
            {'$set': {'Transported': True}}
        )
        all_num = mongo.count()
        processed = mongo.count({'Transported': {'$exists': True}})
        print('Progress: {:.2%}'.format(processed / all_num))

if __name__ == '__main__':
    mongo2postgres()
