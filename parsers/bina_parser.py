import requests
from bs4 import BeautifulSoup

def parse_bina_ads():
    url = "https://bina.az/baki/sah-ismayil-xetai/alqi-satqi/menziller/yeni-tikili/1-otaqli"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Ошибка при запросе к сайту: {response.status_code}")
        return []
    
    soup = BeautifulSoup(response.content, 'html.parser')

    ads = []
    ad_elements = soup.find_all('div', class_='items-i')

    for ad in ad_elements:
        try:
            # Извлечение данных из объявления
            title = ad.find('ul', class_='name').get_text(separator=', ').strip()
            price = ad.find('div', class_='price').get_text(separator=' ').strip()
            link = ad.find('a', class_='item_link')['href']
            location = ad.find('div', class_='location').text.strip()

            ad_data = {
                'title': title,
                'price': price,
                'location': location,
                'link': f"https://bina.az{link}"
            }
            ads.append(ad_data)
        except AttributeError as e:
            print("Ошибка при парсинге элемента объявления. Пропускаем.", e)

    return ads