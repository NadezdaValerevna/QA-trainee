import pytest
import requests

# id,sellerId,name,price,statistics,createdAt ; likes, viewCount, contacts = поля объявления

#Создать объявления
class TestAdCreation:
    BASE_URL = "https://qa-internship.avito.com"

    @pytest.mark.parametrize("seller_id,name,price,likes,views,contacts,number", [
        (111111, "iPhone 13", 65000, 21, 11, 43, 1),  # граничное значение min
        (999999, "MacBook Pro", 120000, 15, 8, 12, 2),  # граничное значение max
    ])

    def test_AdCreation_positive(self, seller_id, name, price, likes, views, contacts, number):
        create_data = {
            "sellerID": seller_id,
            "name": name,
            "price": price,
            "statistics": {
                "likes": likes,
                "viewCount": views,
                "contacts": contacts
            }
        }

        create_response = requests.post(f"{self.BASE_URL}/api/1/item", json=create_data)
        print(f"Позитивный тест #{number}")
        print(f"Response: {create_response.text}")

        assert create_response.status_code in [200, 201], \
            f"Ошибка создания {name}: {create_response.status_code} - {create_response.text}"

    @pytest.mark.parametrize("seller_id,name,price,likes,views,contacts,number", [
        (111110, "AirPods", 15000, 8, 5, 3, 1),  # недопустимое значение -
        (1000000, "Samsung Galaxy", 45000, 12, 7, 9, 2),  # недопустимое значение -
        (111116, "Lenovo", -15000, 8, 5, 3, 3),  # отрицательная цена -
        (115116, "MSI", 150006666666666666666666, 8, 5, 3, 4),  # слишком большая цена
        (115116, 11, 150006666666666666666666, 8, 5, 3, 5),  # вместо названия число
    ])

    def test_AdCreation_negative(self, seller_id, name, price, likes, views, contacts, number):
        create_data = {
            "sellerID": seller_id,
            "name": name,
            "price": price,
            "statistics": {
                "likes": likes,
                "viewCount": views,
                "contacts": contacts
            }
        }

        create_response = requests.post(f"{self.BASE_URL}/api/1/item", json=create_data)
        print(f"Негативный тест #{number}")
        print(f"Response: {create_response.text}")

        # Для негативных тестов ожидаем ошибку
        assert create_response.status_code == 400, \
            f"Ожидалась ошибка 400 для невалидных данных: {create_response.status_code} - {create_response.text}"

#Получить объявления по его идентификатору
class TestAdGet:
    BASE_URL = "https://qa-internship.avito.com"

    @pytest.mark.parametrize("ad_id,number", [
        ("8c057a80-adbe-4874-b749-24487d4f1d89", 1),
        ("6fd5a3c4-24d2-4797-a1e1-1ee9e2adf9cc", 2),
        ("9d617f1d-0c01-4dc9-9a77-8f732086ce8f", 3),
        ("4dc62b1d-154d-4642-a714-9f3f810e3f7a", 4),
        ("ca95413b-d88f-41bc-bf4f-2ed8035ba4a7", 5),
    ])
    def test_AdGet_positive(self, ad_id, number):
        response = requests.get(f"{self.BASE_URL}/api/1/item/{ad_id}")

        print(f"Позитивный тест #{number}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

        assert response.status_code == 200, f"Объявление не найдено! Status: {response.status_code}"

        ad_data = response.json()
        assert isinstance(ad_data, list), f"Ожидался массив, получили: {type(ad_data)}"
        assert len(ad_data) > 0, "Массив объявлений пустой"

    @pytest.mark.parametrize("ad_id,number", [
        ("8c057a80-adbe-4874-b749-24487d4f1d00", 1),  # такого объявления нет
    ])


    def test_AdGet_negative(self, ad_id, number):
        response = requests.get(f"{self.BASE_URL}/api/1/item/{ad_id}")

        print(f"Негативный тест #{number}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

        # Для несуществующего объявления может быть 200 с пустым массивом или 404
        if response.status_code == 200:
            ad_data = response.json()
            assert isinstance(ad_data, list), "Ответ должен быть массивом"
            assert len(ad_data) == 0, "Для несуществующего объявления массив должен быть пустым"
        elif response.status_code == 404:
            print("Несуществующее объявление - 404 Not Found (ожидаемо)")
        else:
            pytest.fail(f"Неожиданный статус код: {response.status_code}")

#Получить все объявления по идентификатору продавца
class TestAdGetForSellerID:
    BASE_URL = "https://qa-internship.avito.com"

    @pytest.mark.parametrize("sellerid,number", [
        (111111, 1),  # продавец существует
        (999999, 2),  # продавец существует
    ])
    def test_AdGetSeller_positive(self, sellerid, number):
        response = requests.get(f"{self.BASE_URL}/api/1/{sellerid}/item")

        print(f"Позитивный тест #{number}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

        assert response.status_code == 200, f"Запрос должен возвращать 200"

        ad_data = response.json()
        assert isinstance(ad_data, list), "Ответ должен быть массивом"
        assert len(ad_data) > 0, "Массив не должен быть пустым"

    @pytest.mark.parametrize("sellerid,number", [
        (111110, 1),  # невалидный -
        (1000000, 2),  # невалидный -
        (123116, 3),  # несуществующий
        (115116, 4),  # несуществующий
    ])
    def test_AdGetSeller_negative(self, sellerid, number):
        response = requests.get(f"{self.BASE_URL}/api/1/{sellerid}/item")

        print(f"Негативный тест #{number}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

        assert response.status_code == 200, f"Запрос должен возвращать 200"

        ad_data = response.json()
        assert isinstance(ad_data, list), "Ответ должен быть массивом"
        assert len(ad_data) == 0, "Для невалидного/несуществующего sellerID массив должен быть пустым"




#Получить статистику по айтем id
class TestAdGetStatistics:
    BASE_URL = "https://qa-internship.avito.com"

    @pytest.mark.parametrize("item_id,number", [
        ("8c057a80-adbe-4874-b749-24487d4f1d89", 1),
        ("6fd5a3c4-24d2-4797-a1e1-1ee9e2adf9cc", 2),
        ("9d617f1d-0c01-4dc9-9a77-8f732086ce8f", 3),
    ])
    def test_GetItemStatistics_positive(self, item_id, number):

        response = requests.get(f"{self.BASE_URL}/api/1/statistic/{item_id}")

        print(f"Позитивный тест #{number}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

        assert response.status_code == 200, f"Запрос должен возвращать 200"

        statistics_list = response.json()
        assert isinstance(statistics_list, list), "Ответ должен быть массивом"
        assert len(statistics_list) > 0, "Массив статистики не должен быть пустым"

        statistics = statistics_list[0]
        expected_fields = ["likes", "viewCount", "contacts"]

        for field in expected_fields:
            assert field in statistics, f"В статистике должно быть поле {field}"
            assert isinstance(statistics[field], int), f"Поле {field} должно быть числом"

        print(f"Статистика получена: {statistics}")

    @pytest.mark.parametrize("item_id,number", [
        ("00000000-0000-0000-0000-000000000000", 1),  # несуществующий
        ("invalid-item-id-123", 2),  # невалидный ID -
    ])
    def test_GetItemStatistics_negative(self, item_id, number):
        """Негативные тесты получения статистики"""
        response = requests.get(f"{self.BASE_URL}/api/1/statistic/{item_id}")

        print(f"Негативный тест #{number}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")


        #Для невалидных ID может быть 200 с пустым массивом или 404
        if response.status_code == 200:
           statistics_list = response.json()
           assert len(statistics_list) == 0, "Для невалидного ID массив статистики должен быть пустым"
        elif response.status_code == 404:
            print(" Несуществующий item - 404 Not Found ")
        else:
           pytest.fail(f"Неожиданный статус код: {response.status_code}")







