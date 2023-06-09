import requests
from bs4 import BeautifulSoup

def find_wiki_path(start_url, end_url, max_depth, language):

    #Добавляем все посещённые страницы в множество (дополнительное игнорирование посещения дублированных ссылок)
    visited = set()
    queue = [(start_url, [])]

    #Цикл будет работать то тех пор, пока список queue не окажется пустым. При каждой итерации получаем первый элемент списка и удаляем его из списка
    while queue:
        #Берём первую в списке ссылку, проверяем, посещали ли мы её, совпадает ли она с конечной, а также проверяем глубину поиска по длине спика path:
        url, path = queue.pop(0)

        print(f"Проверяем {url}") # вывод информации для отладки кода

        if url in visited:
            continue


        visited.add(url)

        #Здесь цикл прерывается, если искомый путь найден
        if url == end_url:
            return path + [url]
        
        #Если достигнута максимальная глубина (длина цепочки url'ов), то новые ссылки перестанут добавляться в список queue на их просмотр)
        if len(path) >= max_depth:
            continue
        
        #Проходим по ссылке url, находим на странице все ссылки: внутренние - по тегам 'a', которые находятся внутри тега 'div' с классом 'mw-body-content mw-content-ltr' 
        # и внешние - внутри тегов 'a' с классом 'external text' - блок References)
        # и добавляем все эти ссылки в список очередь на просмотр
        try:
            req = requests.get(url)
            if not req.ok:
                continue
            soup = BeautifulSoup(req.text, 'html.parser')

            # при выполнении этой команды иногда возвращается ошибка, связанная с тем, что страница на Википедии не оформлена, поэтому эта часть кода обернута в конструкцию try - except
            page_body = soup.find('div', {'class': 'mw-body-content mw-content-ltr'}) 
            links = [a.get('href') for a in page_body.find_all('a', href=True)]
            refs = [a.get('href') for a in page_body.find_all('a', {'class': 'external text'}, href=True)]

            #Оставляем только ссылки на Википедию, убираем дубликаты приведением ко множеству set
            urls = set(filter(lambda link: link and link.startswith('/wiki/'), links + refs))

            for new_url in urls:
                queue.append((f'https://{language}.wikipedia.org{new_url}', path + [url]))
        except Exception as ex:
            print(ex)

    return None

def main():

    start_url = 'https://ru.wikipedia.org/wiki/Python' #начальный url
    end_url = 'https://ru.wikipedia.org/wiki/Байт-код_Java' #конечный url

    language = start_url[8:10] # получаем язык статей из начального url
    max_depth = 5 #указываем максимальную глубину поиска

    path = find_wiki_path(start_url, end_url, max_depth, language)

    if path:
        print(' -> '.join(path))
    else:
        print('Путь не найден')

if __name__ == '__main__':
    main()