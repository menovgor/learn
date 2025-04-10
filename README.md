# ЮрКонструктор - Интеллектуальный конструктор юридических документов

Проект представляет собой веб-приложение для автоматизированного создания процессуальных юридических документов с использованием искусственного интеллекта для российской юрисдикции.

## Описание проекта

ЮрКонструктор - это сервис, который позволяет пользователям создавать юридические документы на основе заполненных анкет. Система задает пользователю необходимые вопросы, собирает данные и генерирует готовый документ, который затем можно улучшить с помощью ИИ, получить юридическую консультацию и проанализировать силу правовой позиции.

### Основные функции

1. **Интерактивное анкетирование** - пошаговый сбор информации для создания документа
2. **Генерация документов** - автоматическое создание юридического документа на основе шаблона и введенных данных
3. **Улучшение с помощью ИИ** - оптимизация текста документа с использованием GPT-4o
4. **Юридическая консультация** - получение рекомендаций по улучшению документа с правовой точки зрения
5. **Анализ правовой позиции** - оценка силы юридических аргументов и шансов на успех
6. **Экспорт в PDF** - скачивание готового документа в формате PDF

## Технологический стек

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **ИИ**: OpenAI GPT-4o API
- **Генерация PDF**: WeasyPrint
- **Дополнительные библиотеки**: num2words (для конвертации чисел в текст)

## Структура проекта

```
legal_doc_generator/
│
├── app.py                  # Основной файл приложения
├── config.py               # Конфигурационные настройки
├── templates/              # HTML шаблоны
│   ├── index.html          # Главная страница
│   ├── questionnaire.html  # Анкета для сбора данных
│   ├── document.html       # Страница предпросмотра документа
│   └── layout.html         # Базовый шаблон
│
├── static/                 # Статические файлы
│   ├── css/style.css       # Стили
│   ├── js/main.js          # JavaScript
│   └── img/                # Изображения (если есть)
│
├── document_templates/     # Шаблоны документов
│   └── debt_collection.txt # Шаблон для взыскания задолженности
│
├── utils/                  # Утилиты
│   ├── document_generator.py # Генератор документов
│   ├── validator.py        # Валидация данных
│   └── ai_service.py       # Интеграция с ИИ
│
└── README.md
```

## Установка и запуск

1. Клонировать репозиторий:
```
git clone https://github.com/username/legal_doc_generator.git
cd legal_doc_generator
```

2. Создать виртуальное окружение и установить зависимости:
```
python -m venv venv
source venv/bin/activate  # для Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Создать файл `.env` в корневой директории проекта:
```
DEBUG=True
SECRET_KEY=your-secret-key
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4o
```

4. Запустить приложение:
```
python app.py
```

5. Открыть в браузере http://127.0.0.1:5000/

## Требования

- Python 3.8 или выше
- OpenAI API ключ
- Установленные зависимости (Flask, WeasyPrint, num2words, python-dotenv, openai)

## Возможности расширения проекта

1. **Добавление новых типов документов** - расширение списка поддерживаемых юридических документов
2. **Внедрение базы данных** - сохранение пользовательских данных и созданных документов
3. **Аутентификация и авторизация** - добавление системы пользователей с различными ролями
4. **Интеграция с правовыми базами данных** - подключение к системам типа КонсультантПлюс или Гарант для проверки актуальности законодательства
5. **Расширенная аналитика** - более глубокий анализ юридической позиции с учетом судебной практики
6. **Система шаблонов** - возможность создания и редактирования собственных шаблонов документов

## Перспективы развития проекта

- **Многоязычная поддержка** - добавление поддержки других юрисдикций и языков
- **Системы управления версиями документов** - отслеживание изменений и версионирование документов
- **Интеграция с электронными системами судов** - возможность прямой подачи документов в суд
- **ИИ-ассистент для консультаций** - чат-бот для ответов на правовые вопросы

## Автор

Проект разработан в рамках магистерской программы Legal Tech.
