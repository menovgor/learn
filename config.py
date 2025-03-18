import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# Настройки приложения
DEBUG = os.getenv('DEBUG', 'True') == 'True'
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-for-development')

# Настройки OpenAI API
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o')  # Используем более доступную модель

# Настройки документов
DOCUMENT_TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'document_templates')