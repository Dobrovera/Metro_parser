import requests
import bs4
import pandas

# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.action_chains import ActionChains


link_to_coffee = 'https://online.metro-cc.ru/category/chaj-kofe-kakao/kofe?from=under_search'
show_more_button_class = 'subcategory-or-type__load-more'
product_class = 'catalog-2-level-product-card'


def parse_metro_categories(category_link):
    request = requests.get(category_link)

    if request.status_code == 200:
        soup = bs4.BeautifulSoup(request.text, 'html.parser')
        products = soup.find_all('div', product_class)

        data_list = []

        for product in products:
            product_id = product['data-sku']
            name = product.find('span', 'product-card-name__text').text.strip()
            link = 'https://online.metro-cc.ru' + product.find('a', 'product-card-photo__link')['href']

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
            # brand = product.find('span', '').text.strip()

            data_list.append({
                'id': product_id,
                'name': name,
                'link': link,
                'regular_price': regular_price,
                'promo_price': promo_price,
                # 'brand': brand
            })

        print(data_list)
        print(len(products))
        df = pandas.DataFrame(data_list)
        df.to_excel('coffee_metro.xlsx', index=False)
        return data_list


parse_metro_categories(link_to_coffee)

# <div class="product-unit-prices__actual-wrapper"
# <div class="product-unit-prices__old-wrapper"
# <a data-qa="product-card-name" href="/products/art_619918" target="_self" title="Кофе Nescafe Gold Barista растворимый сублимированный с добавлением натурального молотого кофе, 400г" class="product-card-name reset-link catalog-2-level-product-card__name style--catalog-2-level-product-card" data-v-22e0f5c0="" data-v-179a6f69="" style="--removed-lines: 0;"><span class="product-card-name__text" data-v-22e0f5c0="">
#     Кофе Nescafe Gold Barista растворимый сублимированный с добавлением натурального молотого кофе, 400г
#   </span> <!----></a>
# <div data-sku="619918" class="catalog-2-level-product-card product-card subcategory-or-type__products-item with-rating with-prices-drop" data-v-179a6f69="" data-v-547e2261=""><div class="product-card__content" data-v-179a6f69=""><div class="base-tooltip product-like catalog-2-level-product-card__like bottom-left style--catalog-2-level-product-card-like can-close-on-click-outside style--catalog-2-level-product-card" data-v-0732e8a8="" data-v-f1726d34="" data-v-179a6f69=""><button data-js-tooltip-trigger="" type="button" class="base-tooltip__trigger reset-button" data-v-0732e8a8=""><div class="product-like__trigger" data-v-0732e8a8="" data-v-f1726d34=""><div class="product-like__icon" data-v-0732e8a8="" data-v-f1726d34=""></div> <!----></div></button> <div data-js-tooltip-content="" class="base-tooltip__content" data-v-0732e8a8=""><div class="base-tooltip__text" data-v-0732e8a8="">
# <button type="button" class="rectangle-button reset--button-styles subcategory-or-type__load-more best-blue-outlined medium normal" data-v-547e2261=""><span>
#         Показать ещё
#       </span> <!----></button>