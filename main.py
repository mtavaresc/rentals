from datetime import datetime
from math import ceil

import requests
from bs4 import BeautifulSoup

from model import Session, Rentals

begin = datetime.now().replace(microsecond=0)
session = Session()

# Input Parameters
max_value = 1300
min_bed = 2
min_bath = 2
min_lot = 1
neighborhoods = ['Sapiranga', 'Passaré', 'Messejana', 'Cidade dos Funcionários', 'Cambeba',
                 'Engenheiro Luciano Cavalcante', 'Cajazeiras', 'Salinas', 'Água Fria',
                 'Parque Iracema', 'José de Alencar']

url = f'https://ce.olx.com.br/fortaleza-e-regiao/fortaleza/imoveis/aluguel/apartamentos' \
      f'?bas={min_bath}&gsp={min_lot}&pe={max_value}&ros={min_bed}'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/80.0.3987.122 '
                         'Safari/537.36'}
results = requests.get(url, headers=headers)
soup = BeautifulSoup(results.text, 'html.parser')
total = soup.find('span', class_='counter').text
total = int(total.split()[4].replace('.', ''))
pages = ceil(total / 50)
f = 0

for page in range(1, pages + 1):
    re = requests.get(f'{url}&o={page}', headers=headers)
    s = BeautifulSoup(re.text, 'html.parser')

    items = s.find_all('li', class_='item')
    for item in items:
        item_id = item.get('data-list_id', None)
        if item_id:
            neighborhood = item.find('p', class_='text detail-region').text
            neighborhood = neighborhood.split(',')[1].strip()

            link = item.find(id=item_id).get('href')
            if neighborhood in neighborhoods:
                d = item.find('p', class_='text detail-specific').text.strip()
                beds = int(d.split(' | ')[[i for i, v in enumerate(d.split(' | ')) if 'quartos' in v][0]].split(
                    ' ')[0]) if len([i for i, v in enumerate(d.split(' | ')) if 'quartos' in v]) == 1 else 0
                area = int(d.split(' | ')[[i for i, v in enumerate(d.split(' | ')) if 'm²' in v][0]].split(' ')[
                               0]) if len([i for i, v in enumerate(d.split(' | ')) if 'm²' in v]) == 1 else 0
                cond = int(d.split(' | ')[[i for i, v in enumerate(d.split(' | ')) if 'Condomínio' in v][0]].split(
                    ' ')[2]) if len([i for i, v in enumerate(d.split(' | ')) if 'Condomínio' in v]) == 1 else 0
                lots = int(d.split(' | ')[[i for i, v in enumerate(d.split(' | ')) if 'vaga' in v][0]].split(' ')[
                               0]) if len([i for i, v in enumerate(d.split(' | ')) if 'vaga' in v]) == 1 else 0
                price = item.find('p', class_='OLXad-list-price').text.strip()
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
