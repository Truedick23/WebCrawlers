from pyArango.connection import *
from pyArango.query import AQLQuery
from pyArango.collection import *
import pymongo

def get_movies_mongo_collection():
    client = pymongo.MongoClient()
    return client.felkub.movies

def get_movies_arango_collection():
    conn = Connection(username='root', password='live1998')

def movies2arango():
    movies_mongo = pymongo.MongoClient().felkub.movies
    movies_collection = Connection(username='root', password='live1998')['felkub']['movies']
    for item in movies_mongo.find({'Arangone': {'$exists': False}}):
        movie = movies_collection.createDocument()
        # movie = dict()
        usable_keys = ['Title', 'Nation', 'Length', 'Starring', 'Directors', 'Year',
                       'Genres', 'Rating', 'Tags', 'VotingNum']
        director_keys = list()
        for url in item['DirectorsUrls']:
            director_keys.append(str(url.split('/')[-2]))
        starring_keys = list()
        for url in item['StarringUrls']:
            starring_keys.append(str(url.split('/')[-2]))
        for key in usable_keys:
            movie[key] = item[key]
        movie['DirectorKeys'] = director_keys
        movie['StarringKeys'] = starring_keys

        key = str(item['Url'].split('/')[-2])

        movie._key = key
        movie.save()

        movies_mongo.update_one(
            {'_id': item['_id']},
            {'$set': {'Arangone': True}}
        )

        print(item['Title'])
        print('Progress: {:.2%}'.format(movies_mongo.count({'Arangone': True}) / movies_mongo.count()))


def tags2arango():
    tags_mongo = pymongo.MongoClient().felkub.tags
    tags_collection = Connection(username='root', password='live1998')['felkub']['tags']
    for item in tags_mongo.find({'Arangone': {'$exists': False}}):
        new_item = tags_collection.createDocument()
        # movie = dict()
        usable_keys = ['Name', 'MovieTitles', 'Traits']
        movie_keys = list()
        for url in item['MovieUrls']:
            movie_keys.append(str(url.split('/')[-2]))

        for key in usable_keys:
            new_item[key] = item[key]
        new_item['MovieKeys'] = movie_keys

        key = str(tags_mongo.count({'Arangone': True}))
        new_item._key = key
        new_item.save()

        tags_mongo.update_one(
            {'_id': item['_id']},
            {'$set': {'Arangone': True}}
        )

        print(item['Name'])
        print('Progress: {:.2%}'.format(tags_mongo.count({'Arangone': True}) / tags_mongo.count()))

def genres2arango():
    genres_mongo = pymongo.MongoClient().felkub.genres
    genres_collection = Connection(username='root', password='live1998')['felkub']['genres']
    for item in genres_mongo.find({'Arangone': {'$exists': False}}):
        new_item = genres_collection.createDocument()
        # movie = dict()
        usable_keys = ['Name', 'MovieTitles', 'Traits']

        movie_keys = list()
        for url in item['MovieUrls']:
            movie_keys.append(str(url.split('/')[-2]))

        for key in usable_keys:
            new_item[key] = item[key]
        new_item['MovieKeys'] = movie_keys

        key = str(genres_mongo.count({'Arangone': True}))

        new_item._key = key
        new_item.save()

        genres_mongo.update_one(
            {'_id': item['_id']},
            {'$set': {'Arangone': True}}
        )

        print(item['Name'])
        print('Progress: {:.2%}'.format(genres_mongo.count({'Arangone': True}) / genres_mongo.count()))

def directors2arango():
    directors_mongo = pymongo.MongoClient().felkub.directors
    directors_collection = Connection(username='root', password='live1998')['felkub']['directors']
    for item in directors_mongo.find({'Arangone': {'$exists': False}}):
        new_item = directors_collection.createDocument()
        # movie = dict()
        usable_keys = ['ShortName', 'DirectNum', 'DirectedTitles', 'FullName', 'AverageRating', 'AverageVotes']

        movie_keys = list()
        for url in item['DirectedUrls']:
            movie_keys.append(str(url.split('/')[-2]))

        for key in usable_keys:
            new_item[key] = item[key]
        new_item['MovieKeys'] = movie_keys

        key = str(item['Url'].split('/')[-2])

        new_item._key = key
        new_item.save()

        directors_mongo.update_one(
            {'_id': item['_id']},
            {'$set': {'Arangone': True}}
        )

        print(item['FullName'])
        print('Progress: {:.2%}'.format(directors_mongo.count({'Arangone': True}) / directors_mongo.count()))

class GenreRelation(Edges):
    _validation = {
        'on_save': False,
        'on_set': False,
        'allow_foreign_fields': True # allow fields that are not part of the schema
    }

    _fields = {
        'Name': Field(),
        'Traits': Field()
    }

def starring2arango():
    starring_mongo = pymongo.MongoClient().felkub.starring
    starring_collection = Connection(username='root', password='live1998')['felkub']['starring']
    for item in starring_mongo.find({'Arangone': {'$exists': False}}):
        new_item = starring_collection.createDocument()
        # movie = dict()
        movie_keys = list()
        for url in item['StarredUrls']:
            movie_keys.append(str(url.split('/')[-2]))

        usable_keys = ['ShortName', 'StarNum', 'StarredTitles', 'FullName', 'AverageRating', 'AverageVotes']
        for key in usable_keys:
            new_item[key] = item[key]
        new_item['MovieKeys'] = movie_keys

        key = str(item['Url'].split('/')[-2])

        new_item._key = key
        new_item.save()

        starring_mongo.update_one(
            {'_id': item['_id']},
            {'$set': {'Arangone': True}}
        )

        print(item['FullName'])
        print('Progress: {:.2%}'.format(starring_mongo.count({'Arangone': True}) / starring_mongo.count()))

def create_genres_edges():
    connection = Connection(username='root', password='live1998')
    felkub = connection['felkub']

    movies_collection = felkub['movies']
    genres_collection = felkub['genres']
    genre_relations = felkub['genre_relations']

    genres_search_aql = 'FOR genre IN genres RETURN genre'
    genres = felkub.AQLQuery(genres_search_aql, rawResults=True)

    for genre in genres:
        print(genre)
        keys = genre['MovieKeys']
        for i in range(len(keys) - 1):
            for j in range(1, len(keys)):
                if i != j:

                    movie1 = movies_collection[keys[i]]
                    movie2 = movies_collection[keys[j]]

                    print(movie1['Title'], movie2['Title'])

                    conn = GenreRelation.createEdge()
                    conn.links(movie1, movie2)

                    conn['Name'] = genre['Name']
                    conn['Traits'] = genre['Traits']

                    conn.save()


def test_query():
    aql = 'FOR movie in movies SORT movie.Year LIMIT 5 RETURN movie.Year'
    felkub = Connection(username='root', password='live1998')['felkub']
    queryResult = felkub.AQLQuery(aql, rawResults=True, batchSize=30)
    for title in queryResult:
        print(title)

if __name__ == '__main__':
    '''
    pymongo.MongoClient().felkub.movies.update_many(
        {}, {'$unset': {'Arangone': ''}}
    )
    '''
    create_genres_edges()