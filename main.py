from datetime import datetime
from math import ceil

from selenium.webdriver import Chrome, ChromeOptions

from model import Session, Rentals

begin = datetime.now().replace(microsecond=0)

session = Session()

options = ChromeOptions()
options.add_argument('--headless')
driver = Chrome('chromedriver', options=options)
driver.set_page_load_timeout(60 * 5)  # for slow internet

# Parameters
max_value = 1300
min_bed = 2
min_bath = 2
min_lot = 1
neighbours = ['Sapiranga', 'Passaré', 'Messejana', 'Cidade dos Funcionários', 'Cambeba',
              'Engenheiro Luciano Cavalcante', 'Cajazeiras', 'Guararapes', 'Água Fria',
              'Parque Iracema', 'José de Alencar']

url = f'https://ce.olx.com.br/fortaleza-e-regiao/fortaleza/imoveis/aluguel/apartamentos' \
      f'?bas={min_bath}&gsp={min_lot}&pe={max_value}&ros={min_bed}'

driver.get(url)
total = driver.find_element_by_class_name('counter').text
total = int(total.split()[4].replace('.', ''))
pages = ceil(total / 50)
f = 0
all_id = [item.id for item in session.query(Rentals).all()]

for page in range(1, pages + 1):
    driver.get(f'{url}&o={page}')

    items = driver.find_elements_by_class_name('item')
    for item in items:
        item_id = item.get_attribute('data-list_id')
        if item_id and item_id not in all_id:
            neighbour = driver.find_element_by_xpath(f'//*[@id="{item_id}"]/div[2]/div[2]/p[1]').text
            neighbour = neighbour.split(',')[1].strip()
            if neighbour in neighbours:
                link = driver.find_element_by_id(item_id).get_attribute('href')
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

                print(f'\nLink: {link}')
                print(f'Bedrooms: {bedrooms}')
                print(f'Area: {area} m²')
                print(f'Condominium: R$ {condominium}')
                print(f'Lots: {lots}')
                print(f'Price: R$ {price}')
                print(f'Neighbour: {neighbour}')
                f += 1
                session.merge(Rentals(item_id, link, bedrooms, area, lots, neighbour, condominium, price))
                session.commit()

driver.quit()
session.close()

end = datetime.now().replace(microsecond=0)
print(f'\n\n**********')
print(f'Searched: {total}')
print(f'Filtered: {f}')
print(f'Elapsed time: {end - begin}')