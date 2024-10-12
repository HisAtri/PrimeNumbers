import os
import math
import sqlite3


class Cursor:
    def __init__(self, connection):
        self.connection = connection
        self.cursor = None

    def __enter__(self):
        self.cursor = self.connection.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cursor:
            self.cursor.close()
        if exc_type:
            self.connection.rollback()
        else:
            self.connection.commit()

class SQLite:
    def __init__(self):
        self.db = sqlite3.connect(os.path.join(os.getcwd(), "primenumber.db"))

    def init_table(self):
        with Cursor(self.db) as cursor:
            # 创建表，并将 prime 列设为唯一
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS primes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prime INTEGER NOT NULL UNIQUE
                )
            ''')

    def insert_prime(self, prime):
        with Cursor(self.db) as cursor:
            try:
                cursor.execute('''
                    INSERT INTO primes (prime) VALUES (?)
                ''', (prime,))
            except sqlite3.IntegrityError:
                # 如果 prime 已存在，跳过插入
                print(f"Exist prime number {prime}, skip it.")

    def get_primes(self, _max: int, _from: int = 0, _batch: int = 1000):
        offset = 0
        while True:
            with Cursor(self.db) as cursor:
                # 分页查询质数
                cursor.execute('''
                    SELECT prime FROM primes
                    WHERE prime >= ? AND prime <= ?
                    ORDER BY prime ASC
                    LIMIT ? OFFSET ?
                ''', (_from, _max, _batch, offset))

                rows = cursor.fetchall()

                if not rows:
                    break

                for row in rows:
                    yield row[0]

                offset += _batch


def is_prime(n, db):
    if n <= 1:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False

    # 获取数据库中已存储的质数
    primes = list(db.get_primes(int(math.sqrt(n)), _from=2))

    for prime in primes:
        if n % prime == 0:
            return False
    return True

def main():
    db = SQLite()
    db.init_table()
    db.insert_prime(2)

    n = 3
    while True:
        if is_prime(n, db):
            db.insert_prime(n)
            print(f"Inserted prime: {n}")
        n += 2

if __name__ == "__main__":
    main()
