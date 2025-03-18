import json
import re
import os
from openai import OpenAI
import config
from utils.data_protection import anonymize_data

# Очистка переменных окружения, связанных с прокси
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)

# Создаем клиента OpenAI
client = OpenAI(api_key=config.OPENAI_API_KEY)


def enhance_document(document_text):
    """
    Улучшает текст документа с помощью AI.

    Args:
        document_text (str): Исходный текст документа

    Returns:
        str: Улучшенный текст документа
    """
    try:
        # Анонимизируем данные перед отправкой
        anonymized_text = anonymize_data(document_text)

        prompt = f"""
        Ты - опытный юрист-практик со специализацией в российском гражданском праве. 
        Улучши следующий юридический документ, сохраняя его структуру и основное содержание. 
        Сделай текст более профессиональным, четким и убедительным, используя правильную юридическую терминологию. 
        Исправь любые ошибки и неточности. Не добавляй информацию, которой нет в исходном документе.

        Важно: сохрани расположение всех дат, имен, сумм и числовых значений. 
        Сохрани форматирование документа (отступы, выравнивание абзацев).

        ДОКУМЕНТ:
        ```
        {anonymized_text}
        ```

        Верни только улучшенный текст документа без дополнительных комментариев.
        """

        # Используем новый формат API
        response = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[
                {"role": "system",
                 "content": "Ты - опытный юрист-эксперт, специализирующийся на процессуальных документах в российской юрисдикции."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )

        # Получаем текст первого сообщения
        enhanced_text = response.choices[0].message.content.strip()

        # Удаление кавычек code block если есть
        if enhanced_text.startswith("```") and enhanced_text.endswith("```"):
            enhanced_text = enhanced_text[3:-3].strip()

        # Восстанавливаем оригинальные данные
        # Note: В реальном приложении нужен более сложный механизм восстановления
        # В демо-версии мы просто используем оригинальный шаблон с улучшенной структурой

        return enhanced_text

    except Exception as e:
        print(f"Ошибка при улучшении документа: {e}")
        return document_text + "\n\n[Не удалось улучшить документ. Ошибка API: " + str(e) + "]"


def get_legal_advice(document_text):
    """
    Получает юридическую консультацию по документу.

    Args:
        document_text (str): Текст документа

    Returns:
        str: HTML-форматированный текст с юридической консультацией
    """
    try:
        # Анонимизируем данные перед отправкой
        anonymized_text = anonymize_data(document_text)

        prompt = f"""
        Проанализируй следующий юридический документ и дай рекомендации по его улучшению с правовой точки зрения. 
        Документ составлен в соответствии с российским законодательством.

        Обрати внимание на:
        1. Соответствие законодательству
        2. Обоснованность требований
        3. Доказательную базу
        4. Полноту и точность информации
        5. Потенциальные риски и слабые места

        ДОКУМЕНТ:
        ```
        {anonymized_text}
        ```

        Дай конкретные рекомендации, как улучшить документ и его юридическую силу. 
        Если найдешь правовые ошибки или недостатки, укажи их и предложи решения.
        """

        # Используем новый формат API
        response = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "Ты - опытный практикующий юрист с опытом судебного представительства."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )

        advice_text = response.choices[0].message.content.strip()

        # Преобразование в HTML формат
        html_advice = advice_text.replace('\n\n', '</p><p>')
        html_advice = f"<p>{html_advice}</p>"

        # Форматирование заголовков и списков
        html_advice = re.sub(r'(?m)^#\s+(.*?)$', r'<h4>\1</h4>', html_advice)
        html_advice = re.sub(r'(?m)^##\s+(.*?)$', r'<h5>\1</h5>', html_advice)
        html_advice = re.sub(r'(?m)^(\d+)\.\s+(.*?)$', r'<strong>\1.</strong> \2', html_advice)

        # Выделение важного
        html_advice = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html_advice)
        html_advice = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html_advice)

        return html_advice

    except Exception as e:
        print(f"Ошибка при получении юридической консультации: {e}")
        return "<p>Извините, не удалось получить юридическую консультацию. Пожалуйста, попробуйте позже.</p><p>Ошибка: " + str(
            e) + "</p>"


def analyze_document_strength(document_text):
    """
    Анализирует силу юридической позиции в документе.

    Args:
        document_text (str): Текст документа

    Returns:
        str: HTML-форматированный текст с анализом юридической позиции
    """
    try:
        # Анонимизируем данные перед отправкой
        anonymized_text = anonymize_data(document_text)

        prompt = f"""
        Проведи анализ силы юридической позиции в следующем документе. Оцени шансы на успех в судебном процессе.

        Документ составлен в соответствии с российским законодательством.

        ДОКУМЕНТ:
        ```
        {anonymized_text}
        ```

        В ответе укажи:
        1. Общую оценку позиции по 10-балльной шкале с обоснованием
        2. Сильные стороны позиции
        3. Слабые стороны и потенциальные риски
        4. Возможные контраргументы противоположной стороны
        5. Рекомендации по усилению позиции

        Будь объективным в оценке, основывайся на законах и судебной практике.
        """

        # Используем новый формат API
        response = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[
                {"role": "system",
                 "content": "Ты - опытный юрист-аналитик с глубоким знанием судебной практики и российского законодательства."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2500
        )

        analysis_text = response.choices[0].message.content.strip()

        # Определение общего балла для визуализации
        score_match = re.search(r'(\d+)(?:\s*|\s*[\.,]\s*)(?:из|\/)\s*10', analysis_text)
        score = int(score_match.group(1)) if score_match else 5

        # Преобразование в HTML формат с визуализацией
        html_analysis = f"""<div class="analysis-content">"""

        # Добавление визуальной шкалы
        if score is not None:
            html_analysis += f"""
            <div class="mb-4">
                <h5 class="mb-2">Сила юридической позиции:</h5>
                <div class="position-relative">
                    <div class="progress" style="height: 30px;">
                        <div class="progress-bar {'bg-danger' if score <= 3 else 'bg-warning' if score <= 6 else 'bg-success'}" 
                             role="progressbar" 
                             style="width: {score * 10}%;" 
                             aria-valuenow="{score}" 
                             aria-valuemin="0" 
                             aria-valuemax="10">
                            {score}/10
                        </div>
                    </div>
                </div>
            </div>
            """

        # Основной текст анализа
        html_analysis += analysis_text.replace('\n\n', '</p><p>')
        html_analysis = f"{html_analysis}<p>"

        # Форматирование заголовков и списков
        html_analysis = re.sub(r'(?m)^#\s+(.*?)$', r'</p><h4>\1</h4><p>', html_analysis)
        html_analysis = re.sub(r'(?m)^##\s+(.*?)$', r'</p><h5>\1</h5><p>', html_analysis)

        # Выделение номеров в списках
        html_analysis = re.sub(r'(?m)^(\d+)\.\s+(.*?)$', r'</p><p><strong>\1.</strong> \2', html_analysis)

        # Выделение важного
        html_analysis = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html_analysis)
        html_analysis = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html_analysis)

        html_analysis += "</p></div>"

        return html_analysis

    except Exception as e:
        print(f"Ошибка при анализе силы юридической позиции: {e}")
        return "<p>Извините, не удалось выполнить анализ юридической позиции. Пожалуйста, попробуйте позже.</p><p>Ошибка: " + str(
            e) + "</p>"


def get_document_suggestions(form_data, doc_type):
    """
    Получает подсказки от ИИ для заполнения документа.

    Args:
        form_data (dict): Текущие данные формы
        doc_type (str): Тип документа

    Returns:
        dict: Словарь с подсказками для полей формы
    """
    try:
        # Анонимизируем данные формы
        anonymized_data = {}
        for key, value in form_data.items():
            if isinstance(value, str):
                anonymized_data[key] = "[Обезличенные данные]"
            else:
                anonymized_data[key] = value

        # Сохраняем структуру и типы полей
        form_structure = {}
        for key, value in form_data.items():
            if value:
                form_structure[key] = "заполнено"
            else:
                form_structure[key] = "не заполнено"

        # Конвертация данных формы в JSON для передачи в API
        form_structure_json = json.dumps(form_structure, ensure_ascii=False)

        prompt = f"""
        Ты - юридический ассистент. На основании структуры формы предложи подходящие значения 
        для незаполненных полей для юридического документа типа "{doc_type}".

        Структура формы (заполнено/не заполнено):
        {form_structure_json}

        Предложи значения только для незаполненных полей.
        Нужно вернуть ответ в формате JSON, где ключи - это имена полей, а значения - предлагаемые значения.
        Предложи только по существу, без объяснений.
        """

        # Используем новый формат API
        response = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[
                {"role": "system",
                 "content": "Ты - юрист-консультант, специализирующийся на составлении юридических документов."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        suggestions_text = response.choices[0].message.content.strip()

        # Извлечение JSON из ответа
        try:
            # Поиск JSON в тексте
            json_match = re.search(r'\{[\s\S]*\}', suggestions_text)
            if json_match:
                suggestions_json = json_match.group(0)
                suggestions = json.loads(suggestions_json)
            else:
                suggestions = {}
        except json.JSONDecodeError:
            suggestions = {}

        return suggestions

    except Exception as e:
        print(f"Ошибка при получении подсказок: {e}")
        return {}