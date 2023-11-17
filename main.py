import requests
import bs4
import pandas
import datetime


link_to_coffee = 'https://online.metro-cc.ru/category/chaj-kofe-kakao/kofe?from=under_search&in_stock=1'
product_class = 'catalog-2-level-product-card'
show_more_button_class = 'subcategory-or-type__load-more'


def parse_metro_categories(category_link):
    page_number = 1
    data_list = []

    # Используем менеджер сеансов для повторного использования соединения
    with requests.Session() as session:
        while True:
            # Формируем URL текущей страницы
            current_page_url = f"{category_link}&page={page_number}"

            # Отправляем GET-запрос к текущей странице
            request = session.get(current_page_url)

            # Проверяем успешность запроса
            if request.status_code != 200:
                break

            # Создаем объект BeautifulSoup для парсинга HTML текущей страницы
            soup = bs4.BeautifulSoup(request.text, 'html.parser')

            # Находим все продукты на текущей странице
            products = soup.find_all('div', product_class)

            # Проверяем, есть ли продукты на текущей странице
            if not products:
                break

            # Итерируемся по каждому продукту на текущей странице
            for product in products:
                product_id = product['data-sku']
                name = product.find('span', 'product-card-name__text').text.strip()
                link = 'https://online.metro-cc.ru' + product.find('a', 'product-card-photo__link')['href']

                # Отправляем GET-запрос к странице продукта
                link_request = session.get(link)

                # Проверяем успешность запроса
                if link_request.status_code == 200:
                    # Создаем объект BeautifulSoup для парсинга HTML страницы продукта
                    link_soup = bs4.BeautifulSoup(link_request.text, 'html.parser')

                    # Извлекаем информацию о бренде продукта
                    brand_elem = link_soup.find('meta', {'itemprop': 'brand'})
                    brand = brand_elem.get('content') if brand_elem else None

                # Извлекаем информацию о цене продукта
                regular_price_element = product.find('div', 'product-unit-prices__old-wrapper')
                if regular_price_element:
                    regular_price = regular_price_element.find('span', 'product-price__sum-rubles')
                    regular_price = regular_price.text.strip().replace("&nbsp;", "") if regular_price else None
                else:
                    regular_price = None

                # Извлекаем информацию о промо-цене продукта
                promo_price_element = product.find('div', 'product-unit-prices__actual-wrapper')
                if promo_price_element:
                    promo_price = promo_price_element.find('span', 'product-price__sum-rubles')
                    promo_price = promo_price.text.strip() if promo_price else None
                else:
                    promo_price = None

                # Добавляем информацию о продукте в список
                data_list.append({
                    'id': product_id,
                    'name': name,
                    'link': link,
                    'regular_price': regular_price,
                    'promo_price': promo_price,
                    'brand': brand
                })
                # Выводим последний добавленный продукт и общее количество продуктов (для отладки)
                print(data_list[-1])
                print(len(data_list))

            # Увеличиваем номер страницы для следующего запроса
            page_number += 1

            # Проверяем наличие кнопки "Показать еще"
            show_more_button = soup.find('button', {'class': show_more_button_class})
            if not show_more_button:
                print("No 'Show More' button found. Exiting.")
                break

    # Создаем DataFrame из списка продуктов и сохраняем в Excel-файл
    df = pandas.DataFrame(data_list)
    df.to_excel('coffee_metro.xlsx', index=False)
    return data_list


if __name__ == "__main__":
    # Замеряем время выполнения
    start_time = datetime.datetime.now()
    parse_metro_categories(link_to_coffee)
    end_time = datetime.datetime.now()
    print(f'Время выполнения: {end_time-start_time}')