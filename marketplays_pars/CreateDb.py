import sqlite3

""" Cоздание база данных, запускать если только базы данных нет"""


# Подключение к базе данных
db = sqlite3.connect("marketplace_price.db")

# Создание курсора
cursor = db.cursor()

# Создание таблицы
cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS price_monitoring (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        marketplace     TEXT NOT NULL,
        title           TEXT NOT NULL,
        title_full      TEXT NOT NULL,
        price           INTEGER NOT NULL,
        max_price       INTEGER,
        min_price       INTEGER,
        date            TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        difference      INTEGER
    );
""")

# Сохранение изменений и закрытие базы данных
db.commit()
db.close()
