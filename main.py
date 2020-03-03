from datetime import datetime
from math import ceil

from selenium.webdriver import Chrome, ChromeOptions

from model import Session, Rentals
import os

begin = datetime.now().replace(microsecond=0)

session = Session()

# Clean db when favorite is false
Rentals.clean()

options = ChromeOptions()
options.add_argument('--headless')
driver = Chrome(os.path.join(os.getcwd(), 'chromedriver'), options=options)
driver.set_page_load_timeout(60 * 5)  # for slow internet

# Parameters
max_value = 1300
min_bed = 2
min_bath = 2
min_lot = 1
neighborhoods = ['Sapiranga', 'Passaré', 'Messejana', 'Cidade dos Funcionários', 'Cambeba',
                 'Engenheiro Luciano Cavalcante', 'Cajazeiras', 'Salinas', 'Água Fria',
                 'Parque Iracema', 'José de Alencar']

# https://ce.olx.com.br/fortaleza-e-regiao/fortaleza/imoveis/venda/casas
# https://ce.olx.com.br/fortaleza-e-regiao/fortaleza/imoveis/venda/apartamentos
# https://ce.olx.com.br/fortaleza-e-regiao/fortaleza/imoveis/aluguel/apartamentos
url = f'https://ce.olx.com.br/fortaleza-e-regiao/fortaleza/imoveis/aluguel/apartamentos' \
      f'?bas={min_bath}&gsp={min_lot}&pe={max_value}&ros={min_bed}'

driver.get(url)
total = driver.find_element_by_class_name('counter').text
total = int(total.split()[4].replace('.', ''))
pages = ceil(total / 50)
f = 0

for page in range(1, pages + 1):
    driver.get(f'{url}&o={page}')

    items = driver.find_elements_by_class_name('item')
    for item in items:
        item_id = item.get_attribute('data-list_id')
        if item_id:
            neighborhood = driver.find_element_by_xpath(f'//*[@id="{item_id}"]/div[2]/div[2]/p[1]').text
            neighborhood = neighborhood.split(',')[1].strip()
            link = driver.find_element_by_id(item_id).get_attribute('href')
            if neighborhood in neighborhoods:
                details = driver.find_element_by_xpath(f'//*[@id="{item_id}"]/div[2]/div[1]/p').text
                bedrooms = int(
                    details.split(' | ')[[i for i, s in enumerate(details.split(' | ')) if 'quartos' in s][0]].split(
                        ' ')[0]) if len(
                    [i for i, s in enumerate(details.split(' | ')) if 'quartos' in s]) == 1 else 0
                area = int(
                    details.split(' | ')[[i for i, s in enumerate(details.split(' | ')) if 'm²' in s][0]].split(' ')[
                        0]) if len(
                    [i for i, s in enumerate(details.split(' | ')) if 'm²' in s]) == 1 else 0
                condominium = int(
                    details.split(' | ')[[i for i, s in enumerate(details.split(' | ')) if 'Condomínio' in s][0]].split(
                        ' ')[2]) if len(
                    [i for i, s in enumerate(details.split(' | ')) if 'Condomínio' in s]) == 1 else 0
                lots = int(
                    details.split(' | ')[[i for i, s in enumerate(details.split(' | ')) if 'vaga' in s][0]].split(' ')[
                        0]) if len([i for i, s in enumerate(details.split(' | ')) if 'vaga' in s]) == 1 else 0
                price = driver.find_element_by_xpath(f'//*[@id="{item_id}"]/div[3]/p').text
                price = int(price.split(' ')[1].replace('.', ''))

                print(f'\n#{f + 1}\n{link}')
                print(f'Bedrooms: {bedrooms}')
                print(f'Area: {area} m²')
                print(f'Lots: {lots}')
                print(f'Price: R$ {price:,.2f}')
                print(f'Condominium: R$ {condominium}')
                print(f'Neighborhood: {neighborhood}')
                f += 1
                session.merge(Rentals(item_id, link, bedrooms, area, lots, neighborhood, condominium, price))
                session.commit()

driver.quit()
session.close()

end = datetime.now().replace(microsecond=0)
print(f'\n\n**********')
print(f'Searched: {total}')
print(f'Filtered: {f}')
print(f'Elapsed time: {end - begin}')
