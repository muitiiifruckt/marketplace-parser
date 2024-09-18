import sqlite3
from parser import OzonSellerParse, YandexSellerParse, WbSellerParse

""" Файл который запускает парсер с входеными параметрами"""

def get_existing_prices(cursor, title):
    """ Возвращает максимальную цену и минимальную"""
    cursor.execute("""
        SELECT MAX(price), MIN(price) FROM price_monitoring WHERE title = ?
    """, (title,))
    result = cursor.fetchone()
    return result if result else (0, 0)

def calculate_difference(current_price, max_price):
    """ Возвращает насколько цена изменелась по отношению к максимальной в процентах"""
    if max_price == 0:
        return 0
    return int(((current_price - max_price) / max_price) * 100)

def insert_price_monitoring(marketplace, title, title_full, price, max_price, min_price, difference):
    """ Добавление спарсенных данных в базу данных"""
    with sqlite3.connect('marketplace_price.db') as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO price_monitoring (
                marketplace, title, title_full, price, max_price, min_price, difference
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (marketplace, title, title_full, price, max_price, min_price, difference))
        conn.commit()

def update_price_data(product_name, prices):
    """ Обработка данных перед вставкой в бд"""
    with sqlite3.connect('marketplace_price.db') as conn:
        cursor = conn.cursor()
        for marketplace, (title, price) in prices.items():
            title_full = title
            try:
                price = int(price)
            except ValueError:
                price = 0

            max_price, min_price = get_existing_prices(cursor, product_name)
            if not max_price:
                max_price = 0
            if not min_price:
                min_price = 9999999

            new_max_price = max(max_price, price)
            new_min_price = min(min_price, price) if min_price != 0 else price
            difference = calculate_difference(price, max_price)

            try:
                insert_price_monitoring(marketplace, product_name, title_full, price, new_max_price, new_min_price, difference)
            except Exception as e:
                print(f"Ошибка при записи в базу данных для {marketplace}: {e}")

if __name__ == "__main__":
    """ Главная функция для запуска сбора данных"""
    products = ["копье", "дуршлаг", "красные носки", "леска для спиннинга"]

    for product in products:
        try:
            a = OzonSellerParse(product).parse()
        except Exception as e:
            print(f"Ошибка парсинга с Ozon для '{product}': {e}")
            a = None

        try:
            b = WbSellerParse(product).parse()
        except Exception as e:
            print(f"Ошибка парсинга с Wildberries для '{product}': {e}")
            b = None

        try:
            c = YandexSellerParse(product).parse()
        except Exception as e:
            print(f"Ошибка парсинга с Yandex для '{product}': {e}")
            c = None

        prices = {
            'Ozon': a,
            'Wildberries': b,
            'Yandex': c
        }

        # Фильтрация значений, где не произошло ошибок
        valid_prices = {k: v for k, v in prices.items() if v is not None}

        if valid_prices:
            update_price_data(product, valid_prices)
