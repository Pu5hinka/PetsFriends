from api import PetFriends
from settings import valid_email, valid_password
import os

pf = PetFriends()

### вынесем часто используемые процедуры в отдельные:
def stat_key (email = valid_email, password = valid_password):
    """авторизация"""

    global stat, auth_key
    stat, auth_key = pf.get_api_key(email, password)

    return auth_key


def all_my_pets():
    """ получение списка своих питомцев и ID последнего добавленного своего питомца"""

    global my_pets, pet_id
    _, my_pets = pf.get_list_of_pets (auth_key, "my_pets")

    # если список не пустой, то получаем ID последнего добавленного своего питомца
    if len(my_pets['pets']) > 0:
        pet_id = my_pets['pets'][0]['id']


def get_alien_key():
    """ авторизация "вредителя" - для тестирования на наличие уязвимостей в безопасности API """

    global alien_key
    # Отправляем запрос на авторизацию заранее зарегистрированного злоумышленника и получаем его KEY
    alien_key = stat_key(email = "wsx@ee.ee", password = "wsx")

    print()
    print('KEY вредителя:', alien_key)


def test_get_api_key_for_valid_user():
    """ Проверяем, что запрос API-ключа возвращает статус 200 и в результате содержится слово KEY """

    # Отправляем запрос на авторизацию
    stat_key()

    # Сверяем полученные данные с нашими ожиданиями
    assert stat == 200
    assert 'key' in auth_key


def test_get_all_pets_with_valid_key(filter=''):
    """ Проверяем что запрос всех питомцев возвращает не пустой список.
    запрашиваем список всех питомцев и проверяем что список не пустой.
    Доступное значение параметра filter - 'my_pets' либо '' """

    # Отправляем запрос на авторизацию
    stat_key()

    status, result = pf.get_list_of_pets(auth_key, filter)

    assert status == 200
    assert len(result['pets']) > 0


def test_add_new_pet_with_valid_data(name = 'Барбоскин', animal_type = 'двортерьер',
                                     age ='4', pet_photo = 'images\dog.jpg'):
    """Проверяем что можно добавить питомца с корректными данными"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Отправляем запрос на авторизацию
    stat_key()

    # Добавляем питомца
    status, result = pf.add_new_pet (auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


def test_successful_delete_self_pet ():
    """Проверяем возможность удаления своего питомца"""

    # Отправляем запрос на авторизацию
    stat_key()

    # Получаем список своих питомцев и ID последнего добавленного
    all_my_pets()

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Суперкот", "кот", "3", "images\cat1.jpg")
        all_my_pets()

    # Берём ID последнего добавленного питомца и отправляем запрос на удаление
    status, result = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    all_my_pets()

    # Проверяем что статус ответа равен 200 и в списке питомцев нет ID удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()


def test_successful_update_self_pet_info(name ='Мурзик', animal_type ='Котэ', age = 5):
    """Проверяем возможность обновления информации о питомце"""

    # Отправляем запрос на авторизацию
    stat_key()

    # Получаем список своих питомцев и ID последнего добавленного
    all_my_pets()

    # Если список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info (auth_key, pet_id, name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если список питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")



def test_failed_email():
    """ (1) Проверяем, что запрос авторизации с отсутствующем в базе email не проходит """

    # Отправляем запрос на авторизацию
    stat_key(email = "qwerty@qwerty.qwerty")

    # Ожидаем 403 - доступ запрещен
    assert stat == 403


def test_failed_pass():
    """ (2) Проверяем, что запрос авторизации с неверным паролем не проходит """

    # Отправляем запрос на авторизацию
    stat_key(password = "12345")

    # Ожидаем 403 - доступ запрещен
    assert stat == 403


def test_create_pet_simple(name ='Simple', animal_type ='Doge', age ='0'):
    """ (3) Проверяем что можно просто создать карточку питомца без фото с корректными данными """

    # Отправляем запрос на авторизацию
    stat_key()

    # Создание питомца без фото
    status, result = pf.create_pet_simple (auth_key, name, animal_type, age)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


def test_create_pet_simple_empty(name = '', animal_type = '', age = ''):
    """ (4) Проверяем что можно просто создать карточку питомца с пустыми данными """

    # Отправляем запрос на авторизацию
    stat_key()

    # Создание питомца без фото
    status, result = pf.create_pet_simple(auth_key, name, animal_type, age)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


def test_create_pet_simple_none(name = None, animal_type = None, age = None):
    """ (5) Проверяем что можно просто создать карточку питомца с нулевыми (None) данными"""
    ### карточка создаётся c пустыми данными но тест провален по последнему утверждению '' != None

    # Отправляем запрос на авторизацию
    stat_key()

    # Создание питомца без фото
    status, result = pf.create_pet_simple(auth_key, name, animal_type, age)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    print(status)
    assert result['name'] == name


def test_set_photo(pet_id ='', pet_photo ="images\cats.jpg"):
    """ (6) Проверяем, что можно добавить фото питомцу"""

    # Отправляем запрос на авторизацию
    stat_key()

    # Получаем полный путь файла с фоткой и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Получаем список своих питомцев и ID последнего добавленного
    all_my_pets()

    # Добавляем ему фотку
    status, _ = pf.set_photo(auth_key, pet_id, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200

""" информация для проверяющего ментора!
    этот тест сначала работал, но после ошибки 500 на сервере, 
    тест перестал работать.
    Ошибка: The requested URL was not found on the server,
    хотя все остальные тесты с тем же URL работают нормально"""


def test_update_age_no_integer(name ='Нецелый', animal_type ='Str', age = 'несколько'):
    """ (7) Проверяем возможность обновления информации о питомце c возрастом строкой, а не целым числом"""

    # Отправляем запрос на авторизацию
    stat_key()

    # Получаем список своих питомцев и ID последнего добавленного
    all_my_pets()

    # Если список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info (auth_key, pet_id, name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если список питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")




def test_delete_alien_pet():
    """ (8) Проверяем возможность удаления ЧУЖОГО питомца -
    если тест пройдёт удачно, значит любой авторизованный пользователь
    может удалить карточку любого ЧУЖОГО питомца, зная его ID"""

    # авторизация злоумышленника и печать его KEY
    get_alien_key()

    # Отправляем запрос на свою авторизацию
    stat_key()
    print('мой KEY:', auth_key)

    # Получаем список своих питомцев и ID последнего добавленного
    all_my_pets()

    # отправляем запрос на удаление используя KEY злоумышленника
    status, _ = pf.delete_pet(alien_key, pet_id)

    # Проверяем что статус ответа равен 200 и в списке питомцев нет ID удалённого питомца
    if status == 200:
        print('Найдена уязвимость: любой авторизованный пользователь ' +
               'может удалить любого чужого питомца, зная его ID')

    assert status == 200
    assert pet_id not in my_pets.values()


def test_set_photo_for_alien_pet(pet_id ='', pet_photo ='images/dog.jpg'):
    """ (9) Проверяем, что можно добавить (изменить) фото ЧУЖОМУ питомцу -
    если тест пройдёт удачно, значит любой авторизованный пользователь
    может добавить или поменять фото любого чужого питомца, зная его ID"""

    # авторизация вредителя и печать его KEY
    get_alien_key()

    # Отправляем запрос на свою авторизацию
    stat_key()
    print('мой KEY:', auth_key)

    # Получаем список своих питомцев и ID последнего добавленного
    all_my_pets()
    print(pet_id)

    # Получаем полный путь файла с фоткой и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Пробуем добавить (поменять) фотку используя KEY вредителя
    status, _ = pf.set_photo(alien_key, pet_id, pet_photo)

    if status == 200:
        print('Найдена уязвимость: любой авторизованный пользователь ' +
               'может добавить или поменять фото любого чужого питомца, зная его ID')

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    ### этот тест тоже проходил успешно, но потом перестал работать по тем же причинам что и тест №6



def test_update_alien_pet(name = 'Собака', animal_type = 'корги', age = 5):
    """ (10) Проверяем возможность изменения вредителем информации о ЧУЖОМ питомце -
    если тест пройдёт удачно, значит любой авторизованный пользователь
    может изменить данные любого чужого питомца, зная его ID"""

    # авторизация вредителя и печать его KEY
    get_alien_key()

    # Отправляем запрос на свою авторизацию
    stat_key()
    print('мой KEY:', auth_key)

    # Получаем список своих питомцев и ID последнего добавленного
    all_my_pets()
    print(pet_id)

    # пробуем обновить имя, тип и возраст своего питомца используя KEY вредителя
    status, result = pf.update_pet_info(alien_key, pet_id, name, animal_type, age)

    if status == 200:
        print('Найдена уязвимость: любой авторизованный пользователь ' +
              'может изменить данные любого чужого питомца, зная его ID')

    # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
    assert status == 200
    assert result['name'] == name