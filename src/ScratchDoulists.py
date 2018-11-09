import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from random import choice

top250url = 'https://movie.douban.com/top250?start='
loginUrl = 'https://accounts.douban.com/login?source=movie'
titlesListPath = 'D:/PycharmProjects/WebCrawlers/data/titlelist'

TitleList = list()
YearList = list()
picUrlList = list()
GenresList = list()
LengthsList = list()
TagsList = list()
ImdbIdList = list()
RatingList = list()
VoteNumList = list()
NationList = list()
LanguageList = list()
DirectorList = list()
StarsList = list()

existedImdbIDList = list()
existedNum = 0
totalMovieNum = 0
crawledNum = 0

myHeaders = ["Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
             "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
             "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",
             "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
             "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)"
             ]
params = {'User-Agent': choice(myHeaders)}


def getExisted():
    with open(titlesListPath) as f:
        global existedTitlesList
        existedTitlesList = f.readline().split('|')


def getHTMLText(url):
    r = requests.get(url)
    try:
        r.headers = params
        r.encoding = 'utf-8'
        r.raise_for_status()
        return r.text
    except:
        print(r.status_code)
        return ''


def scratchRank(url):
    for i in range(0, 10):
        scratchRankPageInfo(url, i)


def scratchRankPageInfo(url, pageIndex):
    print('Progress of pages: {} of {}'.format(pageIndex + 1, 10))
    text = getHTMLText(url + str(pageIndex*25))
    soup = BeautifulSoup(text, 'html.parser')
    urlLists = [item.a['href'] for item in soup.find_all(name='div', attrs={'class': 'hd'})]
    print(urlLists)

    movieNum = pageIndex * 25
    totalNum = 250
    for url in urlLists:
        movieNum = movieNum+1
        crawlMovieInfo(url)
        print('Progress of movies: {} of {}'.format(movieNum, totalNum))


def computeTotalNum(urlList):
    global totalMovieNum
    for url in urlList:
        time.sleep(1.5)
        text = getHTMLText(url)
        soup = BeautifulSoup(text, 'html.parser')
        try:
            totalNum = int(soup
                           .find(name='a', attrs={'class': 'active', 'href': url})
                           .span.string[1:-1])
            print('Number of Doulist: ', totalNum)
            totalMovieNum = totalMovieNum + totalNum
        except:
            print('Error connecting ', url)
            continue


def test(url):
    text = getHTMLText(url)
    soup = BeautifulSoup(text, 'html.parser')
    try:
        for item in soup.find_all(name='a', attrs={'class': 'active',
                                                   'href': url}):
            print(item.span.string[1:-1])
    except:
        print('Error occured')


def scratchDoulist(url):
    global totalMovieNum
    text = getHTMLText(url)
    soup = BeautifulSoup(text, 'html.parser')
    try:
        totalNum = int(soup.find(name='div', attrs={'class': 'doulist-filter'}).a.span.string[1:-1])

        numPages = int(totalNum / 25 + 1)
        print(numPages)
        for i in range(numPages):
            time.sleep(1.2)
            scratchDoulistInfo(url + "?start=" + str(i*25))
    except:
        print('Error connecting ', url)
        return

def scratchDoulistInfo(url):
    text = getHTMLText(url)
    soup = BeautifulSoup(text, 'html.parser')
    urlList = list()
    for item in soup.find_all(name='div', attrs={'class': 'title'}):
        urlList.append(item.a['href'])
    for url in urlList:
        time.sleep(0.5)
        crawlMovieInfo(url)


def scratchCategoricalRankInfo(url, type_name, type, interval_id):
    rankUrl = url + 'type_name=' + type_name + '&type=' + type + '&interval_id=' + interval_id + '&action='
    print(rankUrl)
    text = getHTMLText(rankUrl)
    soup = BeautifulSoup(text, "html.parser")
    print(soup.prettify())
    urlList = list()
    for item in soup.find_all(name='div', attrs={'class': 'movie-info'}):
        print(item)
        urlList.append(item.previous_sibling['href'])
    for url in urlList:
        crawlMovieInfo(url)


def crawlMovieInfo(url):
    global crawledNum, totalMovieNum
    text = getHTMLText(url)
    soup = BeautifulSoup(text, 'html.parser')

    try:
        title = soup.find(name='span', attrs={'property': 'v:itemreviewed'}).string
        year = int(soup.find(name='span', attrs={'class': 'year'}).string[1:-1])
        picUrl = soup.find(name='a', attrs={'class': 'nbgnbg'}).img['src']
        rating = soup.find(name='strong', attrs={'class': 'll rating_num', 'property': 'v:average'}).string
        voteNum = soup.find(name='span', attrs={'property': 'v:votes'}).string
        length = soup.find(name='span', attrs={'property': 'v:runtime'})['content']
        tags = '|'.join(i.string for i in soup.find(name='div', attrs={'class': 'tags-body'}).contents[1::2])
        genres = ''
        for genre in soup.find_all(name='span', attrs={'property': 'v:genre'}):
            genres = genres + genre.string + '|'
        genres = genres[0:-1]
        nation = ''
        for item in soup.find_all(name='span', attrs={'class': 'pl'}):
            if item.string == '制片国家/地区:':
                nation = '|'.join(item.next_sibling.string[1:].split(' / '))
        imdbId = ''
        for item in soup.find_all(name='a', attrs={'rel': 'nofollow', 'target': '_blank'}):
            if item.string[0:2] == 'tt':
                imdbId = item.string[2:]
        directorsList = list()
        for item in soup.find_all(name='a', attrs={'rel': 'v:directedBy'}):
            directorsList.append(item.string)
        directors = '|'.join(directorsList)
        starsList = list()
        for item in soup.find_all(name='a', attrs={'rel': 'v:starring'}):
            starsList.append(item.string)
        stars = '|'.join(starsList)

    except:
        print('Someting Not Found')
        totalMovieNum = totalMovieNum - 1
        return

    if imdbId == '':
        totalMovieNum = totalMovieNum - 1
        return

    if title in existedTitlesList:
        print('Already Exists')
        totalMovieNum = totalMovieNum - 1
        return

    crawledNum = crawledNum + 1
    print('\nNo. {} of {}'.format(crawledNum, totalMovieNum))
    print(title)
    print(year)
    print(picUrl)
    print(rating)
    print(voteNum)
    print(length)
    print(tags)
    print(genres)
    print(nation)
    print(imdbId)
    print(directors)
    print(stars)
    print('Progress: {:.2%}'.format(crawledNum / totalMovieNum))

    existedTitlesList.append(title)
    TitleList.append(title)
    YearList.append(year)
    picUrlList.append(picUrl)
    RatingList.append(rating)
    VoteNumList.append(voteNum)
    LengthsList.append(length)
    TagsList.append(tags)
    GenresList.append(genres)
    NationList.append(nation)
    ImdbIdList.append(imdbId)
    DirectorList.append(directors)
    StarsList.append(stars)



def main():
    '''
    urlList = ['https://www.douban.com/doulist/240962/']
    test('https://www.douban.com/doulist/240962/')
    '''

    with open(titlesListPath, 'r', encoding='utf-8') as f:
        global existedTitlesList
        existedTitlesList = f.readline().split('|')[1:]
    global existedNum
    existedNum = len(existedTitlesList)

    douLists = ['https://www.douban.com/doulist/240962/', 'https://www.douban.com/doulist/243559/',
                'https://www.douban.com/doulist/248893/', 'https://www.douban.com/doulist/2443408/',
                'https://www.douban.com/doulist/4250734/', 'https://www.douban.com/doulist/39587050/',
                'https://www.douban.com/doulist/36879216/', 'https://www.douban.com/doulist/4253902/',
                'https://www.douban.com/doulist/38527265/', 'https://www.douban.com/doulist/37750822/',
                'https://www.douban.com/doulist/38616900/', 'https://www.douban.com/doulist/13699233/',
                'https://www.douban.com/doulist/38968522/', 'https://www.douban.com/doulist/4700408/',
                'https://www.douban.com/doulist/4408143/', 'https://www.douban.com/doulist/5509096/',
                'https://www.douban.com/doulist/11393796/', 'https://www.douban.com/doulist/4337109/',
                'https://www.douban.com/doulist/3575523/', 'https://www.douban.com/doulist/4363132/',
                'https://www.douban.com/doulist/4254982/'][9:]
    print(douLists)

    computeTotalNum(douLists)
    print(totalMovieNum)
    for url in douLists:
        scratchDoulist(url)

    idList = range(existedNum + 1, existedNum + 1+ len(TitleList))

    print(len(TitleList), len(YearList), len(picUrlList), len(GenresList),
          len(LengthsList), len(TagsList), len(ImdbIdList), len(RatingList),
          len(VoteNumList), len(NationList), len(idList), len(DirectorList), len(StarsList))

    data = {
        'ID': idList,
        'Title': TitleList,
        'IMDb': ImdbIdList,
        'Year': YearList,
        'Rating': RatingList,
        'VotingNumber': VoteNumList,
        'Length': LengthsList,
        'Nation': NationList,
        'Genres': GenresList,
        'Tags': TagsList,
        'PictureUrl': picUrlList,
        'Directors': DirectorList,
        'Starring': StarsList
    }

    columns = ['ID', 'Title', 'IMDb', 'Year', 'Ra'
                                              'ting', 'VotingNumber',
               'Length', 'Nation', 'Genres', 'Tags', 'PictureUrl', 'Directors', 'Starring']

    pdFrame = pd.DataFrame(data=data)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)

    pdFrame.to_csv('D:/PycharmProjects/WebCrawlers/data/movies_info_part2'
                   ''
                   '',
                   encoding='utf-8', sep=',', index=False, columns=columns)
    with open(titlesListPath, 'w', encoding='utf-8') as f:
        f.write('|'.join(existedTitlesList))


main()
