import psycopg2
from psycopg2 import errors

def connect(login, password):
    try:
        conn = psycopg2.connect(
            dbname="shop_db",
            user=login,
            password=password,
            host="localhost",
            port="5432"
        )
        return conn
    except Exception as e:
        print(f"\n Ошибка подключения: {e}")
        return None

def call_procedure(conn, query, params=()):
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        print("\n Операция выполнена успешно")
    except errors.InsufficientPrivilege:
        conn.rollback()
        print("\n Ошибка: нет прав для выполнения этой операции")
    except Exception as e:
        conn.rollback()
        print(f"\n Ошибка: {e}")

def get_data(conn, query, params=()):
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        # Читаем NOTICE сообщения
        notices = conn.notices
        if notices:
            for notice in notices:
                print(notice)
        else:
            print("Нет данных")
        conn.commit()
    except errors.InsufficientPrivilege:
        conn.rollback()
        print("\n Ошибка: нет прав для выполнения этой операции")
    except Exception as e:
        conn.rollback()
        print(f"\n Ошибка: {e}")

def show_menu(role):
    print("\n=============================")
    print(f"  Интернет-магазин | {role}")
    print("=============================")
    print("1. Показать товары по категории")
    print("2. Показать заказы покупателя")
    print("3. Добавить товар")
    print("4. Обновить статус заказа")
    print("5. Удалить товар")
    print("0. Выход")
    print("=============================")

def main():
    print("=== Добро пожаловать в систему управления магазином ===")
    login = input("Логин: ")
    password = input("Пароль: ")

    conn = connect(login, password)
    if not conn:
        return

    print(f"\n✅ Подключение успешно! Пользователь: {login}")

    while True:
        show_menu(login)
        choice = input("Выберите действие: ")

        if choice == "1":
            cat_id = input("Введите ID категории (1-Электроника, 2-Одежда, 3-Бытовая техника, 4-Книги, 5-Спорт): ")
            get_data(conn, "CALL get_products_by_category(%s)", (int(cat_id),))

        elif choice == "2":
            cust_id = input("Введите ID покупателя (1-10): ")
            get_data(conn, "CALL get_orders_by_customer(%s)", (int(cust_id),))

        elif choice == "3":
            name = input("Название товара: ")
            price = input("Цена: ")
            stock = input("Количество на складе: ")
            cat_id = input("ID категории: ")
            call_procedure(conn, "CALL insert_product(%s, %s, %s, %s)", (name, float(price), int(stock), int(cat_id)))

        elif choice == "4":
            order_id = input("ID заказа: ")
            status = input("Новый статус (new/processing/shipped/delivered): ")
            call_procedure(conn, "CALL update_order_status(%s, %s)", (int(order_id), status))

        elif choice == "5":
            prod_id = input("ID товара для удаления: ")
            call_procedure(conn, "CALL delete_product(%s)", (int(prod_id),))

        elif choice == "0":
            print("\nДо свидания!")
            break

        else:
            print("\n⚠️ Неверный выбор, попробуйте снова")

    conn.close()

if __name__ == "__main__":
    main()