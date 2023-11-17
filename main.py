import requests
import bs4
import pandas


link_to_coffee = 'https://online.metro-cc.ru/category/chaj-kofe-kakao/kofe?from=under_search&in_stock=1'
product_class = 'catalog-2-level-product-card'
show_more_button_class = 'subcategory-or-type__load-more'


def parse_metro_categories(category_link):
    page_number = 1
    data_list = []

    while True:
        current_page_url = f"{category_link}&page={page_number}"
        request = requests.get(current_page_url)

        if request.status_code != 200:
            break

        soup = bs4.BeautifulSoup(request.text, 'html.parser')
        products = soup.find_all('div', product_class)

        if not products:
            break

        for product in products:
            product_id = product['data-sku']
            name = product.find('span', 'product-card-name__text').text.strip()
            link = 'https://online.metro-cc.ru' + product.find('a', 'product-card-photo__link')['href']

            link_request = requests.get(link)
            if link_request.status_code == 200:
                link_soup = bs4.BeautifulSoup(link_request.text, 'html.parser')
                brand_elem = link_soup.find('meta', {'itemprop': 'brand'})
                brand = brand_elem.get('content') if brand_elem else None

            regular_price_element = product.find('div', 'product-unit-prices__old-wrapper')
            if regular_price_element:
                regular_price = regular_price_element.find('span', 'product-price__sum-rubles')
                regular_price = regular_price.text.strip().replace("&nbsp;", "") if regular_price else None
            else:
                regular_price = None

            promo_price_element = product.find('div', 'product-unit-prices__actual-wrapper')
            if promo_price_element:
                promo_price = promo_price_element.find('span', 'product-price__sum-rubles')
                promo_price = promo_price.text.strip() if promo_price else None
            else:
                promo_price = None

            data_list.append({
                'id': product_id,
                'name': name,
                'link': link,
                'regular_price': regular_price,
                'promo_price': promo_price,
                'brand': brand
            })

        page_number += 1

        show_more_button = soup.find('button', {'class': show_more_button_class})
        if not show_more_button:
            print("No 'Show More' button found. Exiting.")
            break

    df = pandas.DataFrame(data_list)
    df.to_excel('coffee_metro.xlsx', index=False)
    return data_list


parse_metro_categories(link_to_coffee)
