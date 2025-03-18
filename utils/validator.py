import re
import datetime


def validate_inputs(form_data, questions):
    """
    Валидирует данные формы в соответствии с правилами для каждого поля.

    Args:
        form_data (dict): Данные формы
        questions (list): Список вопросов с правилами валидации

    Returns:
        dict: Словарь с ошибками валидации или пустой словарь, если ошибок нет
    """
    errors = {}

    # Собираем все поля из всех секций вопросов
    all_fields = []
    for section in questions:
        all_fields.extend(section['fields'])

    # Проверка обязательных полей
    for field in all_fields:
        if field['required'] and field['name'] not in form_data:
            errors[field['name']] = 'Это поле обязательно для заполнения'
        elif field['required'] and not form_data.get(field['name']):
            errors[field['name']] = 'Это поле обязательно для заполнения'

        # Специальная проверка для ИНН и ОГРН в зависимости от типа лица
        if 'plaintiff_type' in form_data:
            plaintiff_type = form_data['plaintiff_type']

            # ИНН и ОГРН/ОГРНИП обязательны только для юр.лиц и ИП
            if plaintiff_type in ['legal', 'entrepreneur']:
                if not form_data.get('plaintiff_inn'):
                    errors['plaintiff_inn'] = 'ИНН обязателен для юридических лиц и ИП'
                if not form_data.get('plaintiff_ogrn'):
                    errors['plaintiff_ogrn'] = 'ОГРН/ОГРНИП обязателен для юридических лиц и ИП'

    # Проверка правильности форматов
    for field in all_fields:
        field_name = field['name']
        if field_name in form_data and form_data[field_name]:
            # Проверка Email
            if field['type'] == 'email' and not is_valid_email(form_data[field_name]):
                errors[field_name] = 'Некорректный формат email'

            # Проверка дат
            elif field['type'] == 'date' and not is_valid_date(form_data[field_name]):
                errors[field_name] = 'Некорректный формат даты'

            # Проверка ИНН
            elif field_name in ['plaintiff_inn', 'defendant_inn'] and form_data[field_name] and not is_valid_inn(
                    form_data[field_name]):
                errors[field_name] = 'Некорректный формат ИНН'

            # Проверка ОГРН/ОГРНИП
            elif field_name in ['plaintiff_ogrn', 'defendant_ogrn'] and form_data[field_name] and not is_valid_ogrn(
                    form_data[field_name]):
                errors[field_name] = 'Некорректный формат ОГРН/ОГРНИП'

            # Проверка числовых полей
            elif field['type'] == 'number' and not is_valid_number(form_data[field_name]):
                errors[field_name] = 'Поле должно содержать числовое значение'

            # Проверка телефона
            elif field_name == 'plaintiff_phone' and not is_valid_phone(form_data[field_name]):
                errors[field_name] = 'Некорректный формат телефона'

    # Специальные проверки для конкретных типов документов
    if 'debt_amount' in form_data and form_data['debt_amount']:
        try:
            debt_amount = float(form_data['debt_amount'])
            if debt_amount <= 0:
                errors['debt_amount'] = 'Сумма долга должна быть положительным числом'
        except ValueError:
            errors['debt_amount'] = 'Сумма долга должна быть числом'

    if 'penalty_amount' in form_data and form_data['penalty_amount']:
        try:
            penalty_amount = float(form_data['penalty_amount'])
            if penalty_amount < 0:
                errors['penalty_amount'] = 'Сумма неустойки не может быть отрицательной'
        except ValueError:
            errors['penalty_amount'] = 'Сумма неустойки должна быть числом'

    if 'interest_rate' in form_data and form_data['interest_rate']:
        try:
            interest_rate = float(form_data['interest_rate'])
            if interest_rate < 0 or interest_rate > 100:
                errors['interest_rate'] = 'Процентная ставка должна быть от 0 до 100%'
        except ValueError:
            errors['interest_rate'] = 'Процентная ставка должна быть числом'

    # Проверка соответствия типа суда типам сторон
    if 'plaintiff_type' in form_data and 'defendant_type' in form_data and 'court_type' in form_data:
        plaintiff_type = form_data['plaintiff_type']
        defendant_type = form_data['defendant_type']
        court_type = form_data['court_type']

        if court_type == 'arbitrage' and plaintiff_type == 'individual' and defendant_type == 'individual':
            errors['court_type'] = 'Споры между физическими лицами не относятся к компетенции арбитражного суда'

    return errors


def is_valid_email(email):
    """Проверка корректности email"""
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(pattern, email))


def is_valid_date(date_str):
    """Проверка корректности даты"""
    try:
        datetime.datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def is_valid_inn(inn):
    """Проверка корректности ИНН"""
    if not inn.isdigit():
        return False

    # ИНН физического лица - 12 цифр
    if len(inn) == 12:
        return True

    # ИНН юридического лица - 10 цифр
    if len(inn) == 10:
        return True

    return False


def is_valid_ogrn(ogrn):
    """Проверка корректности ОГРН/ОГРНИП"""
    if not ogrn.isdigit():
        return False

    # ОГРН - 13 цифр
    if len(ogrn) == 13:
        return True

    # ОГРНИП - 15 цифр
    if len(ogrn) == 15:
        return True

    return False


def is_valid_number(number_str):
    """Проверка корректности числа"""
    try:
        float(number_str)
        return True
    except ValueError:
        return False


def is_valid_phone(phone):
    """Проверка корректности телефона"""
    pattern = r'^(\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}$'
    return bool(re.match(pattern, phone)) or len(phone) >= 10