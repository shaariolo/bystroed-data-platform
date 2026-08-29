import csv
import random

# Данные для генерации
categories = ["Пицца", "Бургеры", "Суши", "Напитки", "Десерты"]
names_by_category = {
    "Пицца": ["Маргарита", "Пепперони", "Гавайская", "4 сыра", "Мясная"],
    "Бургеры": ["Чизбургер", "Гамбургер", "Бургер с беконом", "Двойной бургер"],
    "Суши": ["Калифорния", "Филадельфия", "Унаги", "Темпура"],
    "Напитки": ["Кола", "Спрайт", "Фанта", "Лимонад", "Чай"],
    "Десерты": ["Чизкейк", "Тирамису", "Мороженое", "Панна-котта"]
}

def generate_products_csv(filename, num_products):
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['product_id', 'name', 'category', 'price', 'quantity', 'is_active'])

        # Генерация товаров
        for i in range(1, num_products + 1):
            category = random.choice(categories)
            name = f"{category} {random.choice(names_by_category[category])} {random.randint(1, 100)}"
            price = round(random.uniform(100, 3000), 2)
            quantity = random.randint(0, 100)
            is_active = random.choice([True, False])

            writer.writerow([i, name, category, price, quantity, is_active])

        print(f"Сгенерировано {num_products} товаров в файл {filename}.")    

if __name__ == "__main__":
    generate_products_csv('data/products.csv', 100000)                

