import cloudscraper
import pandas as pd 
import re

from bs4 import BeautifulSoup

def filter_(text: str):
    """Фильтр матов"""
    text = text.lower().replace('ё', 'е')
    for w in ['еба', 'хуй', 'хуе']:
        text = text.replace(w, '*'*len(w))
    return ' '.join(['*'*len(w) if '*' in w else w for w in text.split()])

def parser_url(url, headers):
    """Парсит страницы мемов"""
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url, headers=headers).text
    soup = BeautifulSoup(response, 'html.parser')
    post_content_div = soup.find('div', class_='s-post-content')
    return post_content_div.find('p').get_text()

def load_mem(year):
    """Парсит мемы по годам"""
    df_dict = {'title': [], 'url': [], 'views': [], 'year': [], 'image_url': [], 'content': []}

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.198 Safari/537.36"
    }

    for page in range(10):
        try:
            url = f"https://memepedia.ru/tag/{year}/page/{page+1}/"
            scraper = cloudscraper.create_scraper()
            html = scraper.get(url, headers=headers).text
        
            soup = BeautifulSoup(html, "html.parser")

            collections = soup.find_all("div", class_="bb-post-collection")[0]
            post_list = collections.find_all('li', class_="post-item")

            for post in post_list:
                count = post.find('span', class_="post-views").get_text(strip=True)
                count = int(float(count[:-1]) * 1000)

                title = post.find(class_="entry-title").get_text(strip=True)
                url = post.find(class_="entry-title").find('a').get("href")
                image_url = post.find(class_="wp-post-image").get('src')

                cleaned_title = re.sub(r'[^а-яА-ЯёЁ\s]', '', title.lower())
                content = parser_url(url, headers)

                if filter_(cleaned_title).find('*') == -1:
                    df_dict['title'].append(cleaned_title)
                    df_dict['url'].append(url)
                    df_dict['views'].append(count)
                    df_dict['year'].append(year)
                    df_dict['image_url'].append(image_url)
                    df_dict['content'].append(content)

            print(f'Страница номер: {page+1}')
        except:
            print('Парсинг завершен!')
            break

    return pd.DataFrame(df_dict)