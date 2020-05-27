from datetime import datetime
from math import ceil
import re as x

import requests
from bs4 import BeautifulSoup

from model import Session, Rentals, BlackList

begin = datetime.now().replace(microsecond=0)
session = Session()

# Clean data
Rentals.clean()
black_list = session.query(BlackList.id).all()

# Input Parameters
max_value = 1500
min_bed = 2
min_bath = 2
min_lot = 1
neighborhoods = ['Sapiranga', 'Messejana', 'Cidade dos Funcionários', 'Cambeba', 'Engenheiro Luciano Cavalcante',
                 'Água Fria', 'Parque Iracema', 'Alagadi']

url = f'https://ce.olx.com.br/fortaleza-e-regiao/fortaleza/imoveis/aluguel/apartamentos' \
      f'?bas={min_bath}&gsp={min_lot}&pe={max_value}&ros={min_bed}'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/80.0.3987.122 '
                         'Safari/537.36'}
results = requests.get(url, headers=headers)
soup = BeautifulSoup(results.text, 'html.parser')
total = soup.find('span', class_='sc-1mi5vq6-0 gfpAwo').text
total = int(total.split()[4].replace('.', ''))
pages = ceil(total / 50)
f = 0

for page in range(1, pages + 1):
    re = requests.get(f'{url}&o={page}', headers=headers)
    s = BeautifulSoup(re.text, 'html.parser')

    items = s.find_all('li', class_='sc-1fcmfeb-2 ggOGTJ')
    for item in items:
        if item.find('a'):
            item_id = item.find('a').get('data-lurker_list_id', None)
            if item_id in black_list:
                continue
            try:
                neighborhood = item.find('p', class_='fnmrjs-13 hdwqVC').text.split(',')[1].strip()
            except AttributeError:
                continue

            if neighborhood in neighborhoods:
                link = item.find('a').get('href')
                d = item.find('p', class_='jm5s8b-0 jDoirm').text.strip().split(' | ')
                beds = int(x.findall(r'\d+', d[[i for i, v in enumerate(d) if 'quartos' in v][0]])[0]) if len(
                    [i for i, v in enumerate(d) if 'quartos' in v]) == 1 else 0
                area = int(x.findall(r'\d+', d[[i for i, v in enumerate(d) if 'm²' in v][0]])[0]) if len(
                    [i for i, v in enumerate(d) if 'm²' in v]) == 1 else 0
                cond = int(x.findall(r'\d+', d[[i for i, v in enumerate(d) if 'Condomínio' in v][0]])[0]) if len(
                    [i for i, v in enumerate(d) if 'Condomínio' in v]) == 1 else 0
                lots = int(x.findall(r'\d+', d[[i for i, v in enumerate(d) if 'vaga' in v][0]])[0]) if len(
                    [i for i, v in enumerate(d) if 'vaga' in v]) == 1 else 0
                price = item.find('p', class_='fnmrjs-16 jqSHIm').text.strip()
                price = int(price.split(' ')[1].replace('.', ''))

                print(f'\n#{f + 1}\n{link}')
                print(f'Bedrooms: {beds}')
                print(f'Area: {area} m²')
                print(f'Lots: {lots}')
                print(f'Price: R$ {price:,.2f}')
                print(f'Condominium: R$ {cond}')
                print(f'Neighborhood: {neighborhood}')
                f += 1
                session.merge(Rentals(item_id, link, beds, area, lots, neighborhood, cond, price, price + cond))
                session.commit()

session.close()
end = datetime.now().replace(microsecond=0)

print(f'\n\n**********')
print(f'Searched: {total}')
print(f'Filtered: {f}')
print(f'Elapsed time: {end - begin}')
