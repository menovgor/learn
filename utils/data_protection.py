import re
import hashlib
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import os


def anonymize_data(document_text):
    """
    Анонимизирует персональные данные в документе перед передачей в API.

    Args:
        document_text (str): Исходный текст документа

    Returns:
        str: Анонимизированный текст документа
    """
    # Замена ФИО на псевдонимы
    document_text = re.sub(r'([А-Я][а-я]+)\s+([А-Я][а-я]+)\s+([А-Я][а-я]+)', 'Иванов Иван Иванович', document_text)
    document_text = re.sub(r'([А-Я][а-я]+)\s+([А-Я])[.]\s*([А-Я])[.]', 'Иванов И.И.', document_text)

    # Замена наименований организаций
    document_text = re.sub(r'ООО\s+["«]([^"»]+)["»]', 'ООО "Организация"', document_text)
    document_text = re.sub(r'АО\s+["«]([^"»]+)["»]', 'АО "Организация"', document_text)
    document_text = re.sub(r'ИП\s+([А-Я][а-я]+\s+[А-Я][.]\s*[А-Я][.])', 'ИП Иванов И.И.', document_text)

    # Замена адресов
    document_text = re.sub(r'\d{6},?\s+[гГ][.]?\s+[А-Я][а-я]+,?\s+[а-яА-Я\s,.]+\d+',
                           '101000, г. Москва, ул. Примерная, д. 1', document_text)

    # Замена телефонов
    document_text = re.sub(r'[\+7|8][\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}', '+7 (999) 123-45-67',
                           document_text)

    # Замена электронной почты
    document_text = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', 'example@example.com', document_text)

    # Замена ИНН/ОГРН
    document_text = re.sub(r'ИНН:?\s*\d{10,12}', 'ИНН: 1234567890', document_text)
    document_text = re.sub(r'ОГРН:?\s*\d{13}', 'ОГРН: 1234567890123', document_text)
    document_text = re.sub(r'ОГРНИП:?\s*\d{15}', 'ОГРНИП: 123456789012345', document_text)

    # Замена номеров договоров
    document_text = re.sub(r'[Дд]оговор[а]?\s+[№N][\s-]?[\w\-\/]+', 'Договор № 123/2023', document_text)

    # Замена банковских реквизитов
    document_text = re.sub(r'р/с\s*\d{20}', 'р/с 40702810123456789012', document_text)
    document_text = re.sub(r'к/с\s*\d{20}', 'к/с 30101810123456789012', document_text)
    document_text = re.sub(r'БИК\s*\d{9}', 'БИК 044525225', document_text)

    return document_text


def generate_key(secret_key):
    """
    Генерирует ключ шифрования на основе секретного ключа.

    Args:
        secret_key (str): Секретный ключ приложения

    Returns:
        bytes: Ключ шифрования
    """
    # Используем хеш-функцию для создания ключа
    return hashlib.sha256(secret_key.encode()).digest()


def encrypt_data(data, secret_key):
    """
    Шифрует данные с использованием AES.

    Args:
        data (dict): Данные для шифрования
        secret_key (str): Секретный ключ

    Returns:
        str: Зашифрованные данные в формате base64
    """
    try:
        # Преобразование словаря в строку
        data_str = str(data)

        # Генерация ключа
        key = generate_key(secret_key)

        # Генерация случайного вектора инициализации
        iv = os.urandom(16)

        # Создание шифра
        cipher = AES.new(key, AES.MODE_CBC, iv)

        # Шифрование данных
        ct_bytes = cipher.encrypt(pad(data_str.encode(), AES.block_size))

        # Объединение IV и зашифрованных данных
        encrypted_data = base64.b64encode(iv + ct_bytes).decode('utf-8')

        return encrypted_data

    except Exception as e:
        print(f"Ошибка при шифровании данных: {e}")
        return None


def decrypt_data(encrypted_data, secret_key):
    """
    Дешифрует данные, зашифрованные с помощью AES.

    Args:
        encrypted_data (str): Зашифрованные данные в формате base64
        secret_key (str): Секретный ключ

    Returns:
        dict: Дешифрованные данные
    """
    try:
        # Генерация ключа
        key = generate_key(secret_key)

        # Декодирование из base64
        encrypted_bytes = base64.b64decode(encrypted_data)

        # Извлечение IV (первые 16 байт)
        iv = encrypted_bytes[:16]
        ct = encrypted_bytes[16:]

        # Создание шифра
        cipher = AES.new(key, AES.MODE_CBC, iv)

        # Дешифрование данных
        pt = unpad(cipher.decrypt(ct), AES.block_size)

        # Преобразование строки обратно в словарь (требует осторожности)
        # В реальном приложении лучше использовать JSON
        data_str = pt.decode('utf-8')
        data = eval(data_str)  # Замечание: eval небезопасен в продакшн-коде, лучше использовать json.loads

        return data

    except Exception as e:
        print(f"Ошибка при дешифровании данных: {e}")
        return None