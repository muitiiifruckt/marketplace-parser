import json
import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re


""" Здесь написана основная логика парсеров """

class YandexSellerParse:
    """ Парсе яндекс маркета"""
    def __init__(self, keyword: str):
        self.keyword = keyword
    def parse(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False)
            self.context = browser.new_context()
            self.page = self.context.new_page()
            self.page.goto("https://market.yandex.ru/")
            time.sleep(1)
            self.page.get_by_placeholder("Найти товары").nth(0).type(text=self.keyword, delay=2)
            time.sleep(1)
            self.page.get_by_placeholder("Найти товары").nth(0).press("Enter")
            time.sleep(4)
            # Нажать на кнопку по тексту
            if self.page.get_by_text('подешевле').nth(1):
                self.page.get_by_text('подешевле').nth(1).click()
            time.sleep(2)
            # Получение HTML страницы
            html_content = self.page.content()
            soup = BeautifulSoup(html_content, 'html.parser')


            # Найти все элементы с нужными классами для названия
            title_elements = soup.find_all('span', class_='ds-text_lineClamp_2')

            # Найти все элементы с нужными классами для цен
            price_elements = soup.find_all('span', class_='ds-text_weight_bold')

            # Список для хранения информации о товарах
            products = []

            # Убедимся, что у нас есть одинаковое количество названий и цен
            for title_element, price_element in zip(title_elements, price_elements):
                title_text = title_element.get_text(strip=True)
                price_text = price_element.get_text(strip=True)

                # Убедимся, что цена содержит только числовые данные и символ валюты
                if title_text and price_text:
                    try:
                        # Преобразовать цену в число
                        price_value = float(price_text.replace(' ₽', '').replace(',', '.'))
                        products.append({
                            'title': title_text,
                            'price': price_value
                        })
                    except ValueError:
                        continue

            # Найти артикул, если есть
            article_elements = soup.find_all('span', class_='ds-text_weight_med')  # Замените на правильный класс

            for product, article_element in zip(products, article_elements):
                article_text = article_element.get_text(strip=True)
                product['article'] = article_text



            # Найти товар с наименьшей ценой
            if products:
                lowest_price_product = min(products, key=lambda p: p['price'])

            return lowest_price_product["title"],lowest_price_product["price"]


class WbSellerParse:
    """ Парсер вб"""
    def __init__(self, keyword: str):
        self.keyword = keyword
    def parse(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False)
            self.context = browser.new_context()
            self.page = self.context.new_page()
            self.page.goto("https://www.wildberries.ru/")
            time.sleep(3)
            self.page.get_by_placeholder("Найти на Wildberries").nth(0).type(text=self.keyword, delay=2)
            time.sleep(2)
            self.page.get_by_placeholder("Найти на Wildberries").nth(0).press("Enter")
            time.sleep(2)
            self.page.query_selector("button[class='dropdown-filter__btn dropdown-filter__btn--sorter']").click()
            time.sleep(2)
            # Нажатие на span с классом 'radio-with-text__text'
            # Фильтрация по тексту 'По популярности'

            self.page.locator("span.radio-with-text__text").filter(has_text="По возрастанию цены").click()
            time.sleep(2)
            # Нажать на элемент по классу
            self.page.locator("a.product-card__link.j-card-link.j-open-full-product-card").nth(0).click()
            html_content = self.page.content()
            soup = BeautifulSoup(html_content, 'html.parser')

            # Извлечение названия из атрибута aria-label
            product_link = soup.find('a', class_='product-card__link')
            if product_link:
                title = product_link.get('aria-label', 'No Title')
            else:
                title = 'No Title'

            # Извлечение цены
            price_element = soup.find('ins', class_='price__lower-price')

            if price_element:
                # Извлекаем текст и убираем символ валюты и пробелы
                price_text = price_element.get_text(strip=True)
                # Убираем символ валюты и пробелы, а затем преобразуем в число
                price_value = price_text.replace(' ₽', '').replace(',', '.')
                try:
                    price_number = float(price_value.replace("₽",""))
                except ValueError:
                    price_number = 'No Price'
            else:
                price_number = "No Price"
            # Вывод результата
            return title,int(price_number)

class OzonSellerParse:
    """ Парсер Озона"""
    def __init__(self, keyword: str):
        self.keyword = keyword


    def parse(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False)
            self.context = browser.new_context()
            self.page = self.context.new_page()
            self.page.goto("https://www.ozon.ru/?__rr=1")
            time.sleep(4)
            self.page.query_selector("button[id='reload-button']").click()
            time.sleep(5)
            self.page.get_by_placeholder("Искать на Ozon").type(text=self.keyword, delay=2)
            time.sleep(4)

            self.page.query_selector("button[type='submit']").click()
            time.sleep(2)
            if self.page.query_selector("button[id='reload-button']"):
                self.page.query_selector("button[id='reload-button']").click()
            time.sleep(2)
            # Нажать на элемент по title
            self.page.locator('input[title="Популярные"]').click()

            time.sleep(3)
            # Ожидание и клик по элементу с текстом "Дешевле"
            self.page.locator('.b3215-a9.tsCompact500Medium', has_text='Дешевле').click()
            time.sleep(2)
            if self.page.query_selector("button[id='reload-button']"):
                self.page.query_selector("button[id='reload-button']").click()
                time.sleep(1)
            html_content = self.page.content()
            soup = BeautifulSoup(html_content, 'html.parser')
            # Извлечение цены

            price_span = soup.find('span', class_='c3015-a1 tsHeadline500Medium c3015-c0')
            if price_span:
                price_text = price_span.get_text(strip=True)
                # Удаляем нецифровые символы кроме пробелов и символов валюты
                price = re.sub(r'[^\d]', '', price_text)
            else:
                price = 'Цена не найдена'

            # Извлечение названия
            name_a_tag = soup.find('a', class_='tile-hover-target j2m_23 m2j_23')
            if name_a_tag:
                name_span = name_a_tag.find('span', class_='tsBody500Medium')
                name = name_span.get_text(strip=True) if name_span else 'Название не найдено'
            else:
                name = 'Название не найдено'

            return name, price


if __name__ == "__main__":
    """ Модульная проверка работоспособности парсеров"""
    a = OzonSellerParse("копье").parse()
    b = WbSellerParse("копье").parse()
    с = YandexSellerParse("копье").parse()
    print(a)