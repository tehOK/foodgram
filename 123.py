import json
import os

# Путь к исходному файлу относительно текущей директории (где запускается скрипт)
json_path = 'data/ingredients.json'

# Название вашего Django приложения (замените на ваше)
app_label = 'ingredients'  # например, 'recipes'

# Путь к файлу фикстуры, который создадим
fixture_path = 'data/ingredients_fixture.json'

# Загружаем исходные данные
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

fixtures = []

for i, item in enumerate(data, start=1):
    fixture_item = {
        'model': f'{app_label}.ingredient',
        'pk': i,
        'fields': {
            'name': item['name'],
            'measurement_unit': item['measurement_unit']
        }
    }
    fixtures.append(fixture_item)

# Записываем в файл фикстуры
with open(fixture_path, 'w', encoding='utf-8') as f:
    json.dump(fixtures, f, ensure_ascii=False, indent=2)

print(f'Файл фикстуры создан: {fixture_path}')