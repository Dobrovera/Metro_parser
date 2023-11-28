import datetime as dt
import asyncio

import aiohttp
import aiolimiter
import bs4
import prompt

from database import connect, Product


PRODUCT_CLASS = 'catalog-2-level-product-card'
SHOW_MORE_BUTTON_CLASS = 'subcategory-or-type__load-more'


async def scrape(html: str, session: aiohttp.ClientSession):
    # Создаем объект BeautifulSoup для парсинга HTML текущей страницы
    soup = bs4.BeautifulSoup(html, 'html.parser')

    # Находим все продукты на текущей странице
    products = soup.find_all('div', PRODUCT_CLASS)

    # Проверяем, есть ли продукты на текущей странице
    if not products:
        return

    # Итерируемся по каждому продукту на текущей странице
    for product in products:
        product_id = product['data-sku']
        name = product.find('span', 'product-card-name__text').text.strip()
        link = 'https://online.metro-cc.ru' + product.find('a', 'product-card-photo__link')['href']

        # Отправляем GET-запрос к странице продукта
        response: aiohttp.ClientResponse = await session.get(link)

        # Проверяем успешность запроса
        if not response.ok:
            break

        # Считываем контент страницы
        html = await response.text()

        # Создаем объект BeautifulSoup для парсинга HTML страницы продукта
        link_soup = bs4.BeautifulSoup(html, 'html.parser')

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

        # Добавляем информацию о продукте в БД
        await Product.add(
            product_id = product_id,
            name = name,
            link = link,
            regular_price = regular_price,
            promo_price = promo_price,
            brand = brand
        )

        print(f'Продукт {product_id} добавлен в базу данных.')


async def main():
    throttler = aiolimiter.AsyncLimiter(max_rate=1000, time_period=1)   # 1000 задач в секунду

    category_link = prompt.string('Привет! Введи URL категории товара для парсинга:\n')

    await connect()

    # Используем менеджер сеансов для повторного использования соединения
    async with aiohttp.ClientSession() as session:
        page_number = 1
        tasks = []

        async with throttler:
            while True:
                # Формируем URL текущей страницы
                current_page_url = f'{category_link}&page={page_number}'
                print(f'Парсим страницу {page_number}.')

                # Отправляем GET-запрос к текущей странице
                async with session.get(current_page_url) as response:

                    # Проверяем успешность запроса
                    if not response.ok:
                        break

                    # Считываем контент страницы
                    html = await response.text()

                    # Создаем задачу извлечения данных
                    task = asyncio.create_task(scrape(html, session))
                    tasks.append(task)
                    print(f'Задачу на страницу {page_number} поставили.')

                    soup = bs4.BeautifulSoup(html, 'html.parser')
                    # Проверяем наличие кнопки "Показать еще"
                    show_more_button = soup.find('button', {'class': SHOW_MORE_BUTTON_CLASS})
                    if not show_more_button:
                        print('Кнопка «Показать ещё» не найдена. Выход.')
                        break

                # Инкрементируем счетчик
                page_number += 1

            await asyncio.gather(*tasks)

    await Product.export()


if __name__ == "__main__":
    # Замеряем время выполнения
    start_time = dt.datetime.now()
    asyncio.run(main())
    end_time = dt.datetime.now()
    print(f'Время выполнения: {end_time-start_time}')
