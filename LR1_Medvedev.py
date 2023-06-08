import requests
from bs4 import BeautifulSoup
import datetime
import time
import json
 

#получаем id последней на момент запуска новости
def get_last_new(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    news = soup.find('ul', {'class': 'news_list'})
    last_new = next(news.children, None)
    return(last_new.find('a').get('href')[-6:-1])

#получаем все новости с первой страницы
def get_news(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    news_list = soup.find('ul', {'class': 'news_list'})
    news = news_list.find_all('a')
    links = []
    articles = []

    for el in news:
        article = dict()
        num = el.get('href')
        links.append(num[-6:-1])
        link = "https://www.autostat.ru/news/" + num
        title = el.find('h3').text
        annotation = el.find('h3').next_sibling.text

        article['link'] = link
        article['title'] = title
        article['annotation'] = annotation

        articles.append(article)

    return articles, links

def main():
    url = "https://www.autostat.ru/news/"
    key = 'автоваз'
    result = []

    last_id = get_last_new(url)

    start = datetime.datetime.now()
    print(f"Скрипт запущен {start}")

    difference = datetime.datetime.now() - start
    #Ограничиваем время работы скрипта одними сутками
    while divmod(difference.total_seconds(), 3600)[0] < 24:
        print('Ждём 15 минут...')
        time.sleep(900)

        print('Проверяем, если ли новые новости....')
        obj = get_news(url)
        articles, links = obj[0], obj[1]

        if last_id in links:
            #если новость с полученным ранее id стоит на первом месте в полученном списке нововстей, то новых новостей нет
            if links.index(last_id) == 0:
                print('Нет новых записей')
            #иначе, обрезаем список новостей, оставляя только те, которые появились после запуска скрипта
            else:
                print(f"Проверяем, если ли в новых статьях упоминания об '{key}' ...")
                links = links[0:links.index(last_id)]
                articles = articles[0:links.index(last_id)]
                for el in articles:
                    #проверяем, есть ли упоминание ключевого слова в заголовке или аннотации статьи
                    words = (el['title'] + el['annotation']).lower().translate({ord(c): None for c in ',.-()!@#$\n'}).split()
                    if key in words:
                        r = requests.get(el['link'])
                        soup = BeautifulSoup(r.text, 'html.parser')
                        author = soup.find('div', {'class': 'News-author_title'}).find('a').text
                        el['author'] = author
                        print(f'Найдена статья с упоминанием {key}. Выгружаем её.')
                        result.append(el)
                #обновляем id последней новости
                last_id = links[0]
        difference = datetime.datetime.now() - start
        print(divmod(difference.total_seconds(), 3600)[0])

    with open('atricles.txt', 'w') as f:
        for el in result:
            print(el, "\n", file = f)
        
if __name__ == '__main__':
    main()