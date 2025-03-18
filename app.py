from flask import Flask, render_template, request, redirect, url_for, session, send_file
from utils.document_generator import generate_document, generate_pdf
from utils.validator import validate_inputs
from utils.ai_service import enhance_document, get_legal_advice, analyze_document_strength
from utils.data_protection import encrypt_data, decrypt_data, anonymize_data
import datetime
import io
import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY


# Типы документов
DOCUMENT_TYPES = {
    'debt_collection': {
        'name': 'Исковое заявление о взыскании задолженности',
        'description': 'Документ для обращения в суд с требованием о взыскании денежной задолженности с должника.'
    },
    'labor_dispute': {
        'name': 'Исковое заявление по трудовому спору',
        'description': 'Документ для защиты прав работника в случае нарушения трудового законодательства работодателем.'
    },
    'contract_termination': {
        'name': 'Уведомление о расторжении договора',
        'description': 'Документ для одностороннего расторжения договора с соблюдением требований законодательства.'
    },
    'labor_dispute': {
    'name': 'Исковое заявление по трудовому спору',
    'description': 'Документ для защиты прав работника в случае нарушения трудового законодательства работодателем.'
    }
}

# Вопросы для формирования документов
QUESTIONS = {
    'debt_collection': [
        {
            'id': 'plaintiff_info',
            'title': 'Информация об истце',
            'fields': [
                {'name': 'plaintiff_type', 'label': 'Тип истца', 'type': 'select', 'options': [
                    {'value': 'individual', 'label': 'Физическое лицо'},
                    {'value': 'legal', 'label': 'Юридическое лицо'},
                    {'value': 'entrepreneur', 'label': 'Индивидуальный предприниматель'}
                ], 'required': True},
                {'name': 'plaintiff_name', 'label': 'ФИО/Наименование организации', 'type': 'text', 'required': True},
                {'name': 'plaintiff_address', 'label': 'Адрес', 'type': 'text', 'required': True},
                {'name': 'plaintiff_phone', 'label': 'Телефон', 'type': 'text', 'required': True},
                {'name': 'plaintiff_email', 'label': 'Email', 'type': 'email', 'required': False},
                {'name': 'plaintiff_inn', 'label': 'ИНН', 'type': 'text', 'required': False},
                {'name': 'plaintiff_ogrn', 'label': 'ОГРН/ОГРНИП', 'type': 'text', 'required': False}
            ]
        },
        {
            'id': 'defendant_info',
            'title': 'Информация об ответчике',
            'fields': [
                {'name': 'defendant_type', 'label': 'Тип ответчика', 'type': 'select', 'options': [
                    {'value': 'individual', 'label': 'Физическое лицо'},
                    {'value': 'legal', 'label': 'Юридическое лицо'},
                    {'value': 'entrepreneur', 'label': 'Индивидуальный предприниматель'}
                ], 'required': True},
                {'name': 'defendant_name', 'label': 'ФИО/Наименование организации', 'type': 'text', 'required': True},
                {'name': 'defendant_address', 'label': 'Адрес', 'type': 'text', 'required': True},
                {'name': 'defendant_inn', 'label': 'ИНН (если известен)', 'type': 'text', 'required': False},
                {'name': 'defendant_ogrn', 'label': 'ОГРН/ОГРНИП (если известен)', 'type': 'text', 'required': False}
            ]
        },
        {
            'id': 'court_info',
            'title': 'Информация о суде',
            'fields': [
                {'name': 'court_type', 'label': 'Тип суда', 'type': 'select', 'options': [
                    {'value': 'general', 'label': 'Суд общей юрисдикции'},
                    {'value': 'arbitrage', 'label': 'Арбитражный суд'}
                ], 'required': True},
                {'name': 'court_name', 'label': 'Наименование суда', 'type': 'text', 'required': True},
                {'name': 'court_address', 'label': 'Адрес суда', 'type': 'text', 'required': True}
            ]
        },
        {
            'id': 'claim_details',
            'title': 'Детали требования',
            'fields': [
                {'name': 'contract_number', 'label': 'Номер договора', 'type': 'text', 'required': True},
                {'name': 'contract_date', 'label': 'Дата договора', 'type': 'date', 'required': True},
                {'name': 'debt_amount', 'label': 'Сумма основного долга (руб.)', 'type': 'number', 'required': True},
                {'name': 'penalty_amount', 'label': 'Сумма неустойки (руб.)', 'type': 'number', 'required': False},
                {'name': 'interest_rate', 'label': 'Процентная ставка по ст. 395 ГК РФ', 'type': 'number',
                 'required': False},
                {'name': 'claim_circumstances', 'label': 'Обстоятельства возникновения задолженности',
                 'type': 'textarea', 'required': True},
                {'name': 'payment_details', 'label': 'Реквизиты для перечисления средств', 'type': 'textarea',
                 'required': True}
            ]
        },
        {
            'id': 'attachments',
            'title': 'Приложения',
            'fields': [
                {'name': 'has_contract_copy', 'label': 'Копия договора', 'type': 'checkbox', 'required': False},
                {'name': 'has_payment_docs', 'label': 'Документы об оплате госпошлины', 'type': 'checkbox',
                 'required': False},
                {'name': 'has_claim_calculations', 'label': 'Расчет исковых требований', 'type': 'checkbox',
                 'required': False},
                {'name': 'has_pretension', 'label': 'Претензия', 'type': 'checkbox', 'required': False},
                {'name': 'has_correspondence', 'label': 'Переписка сторон', 'type': 'checkbox', 'required': False},
                {'name': 'other_attachments', 'label': 'Иные документы', 'type': 'textarea', 'required': False}
            ]
        }
    ],
    'labor_dispute': [
        {
            'id': 'plaintiff_info',
            'title': 'Информация об истце (работнике)',
            'fields': [
                {'name': 'plaintiff_name', 'label': 'ФИО', 'type': 'text', 'required': True},
                {'name': 'plaintiff_address', 'label': 'Адрес', 'type': 'text', 'required': True},
                {'name': 'plaintiff_phone', 'label': 'Телефон', 'type': 'text', 'required': True},
                {'name': 'plaintiff_email', 'label': 'Email', 'type': 'email', 'required': False}
            ]
        },
        {
            'id': 'defendant_info',
            'title': 'Информация об ответчике (работодателе)',
            'fields': [
                {'name': 'defendant_name', 'label': 'Наименование организации', 'type': 'text', 'required': True},
                {'name': 'defendant_address', 'label': 'Адрес', 'type': 'text', 'required': True},
                {'name': 'defendant_inn', 'label': 'ИНН', 'type': 'text', 'required': False},
                {'name': 'defendant_ogrn', 'label': 'ОГРН', 'type': 'text', 'required': False}
            ]
        },
        {
            'id': 'court_info',
            'title': 'Информация о суде',
            'fields': [
                {'name': 'court_name', 'label': 'Наименование суда', 'type': 'text', 'required': True},
                {'name': 'court_address', 'label': 'Адрес суда', 'type': 'text', 'required': True}
            ]
        },
        {
            'id': 'employment_details',
            'title': 'Сведения о трудовых отношениях',
            'fields': [
                {'name': 'position', 'label': 'Должность', 'type': 'text', 'required': True},
                {'name': 'employment_start_date', 'label': 'Дата начала работы', 'type': 'date', 'required': True},
                {'name': 'employment_end_date', 'label': 'Дата окончания работы (если применимо)', 'type': 'date',
                 'required': False},
                {'name': 'contract_number', 'label': 'Номер трудового договора', 'type': 'text', 'required': True},
                {'name': 'contract_date', 'label': 'Дата заключения трудового договора', 'type': 'date',
                 'required': True},
                {'name': 'salary', 'label': 'Размер заработной платы (руб.)', 'type': 'number', 'required': False}
            ]
        },
        {
            'id': 'dispute_info',
            'title': 'Информация о трудовом споре',
            'fields': [
                {'name': 'dispute_type', 'label': 'Тип спора', 'type': 'select', 'options': [
                    {'value': 'unpaid_salary', 'label': 'Взыскание невыплаченной заработной платы'},
                    {'value': 'illegal_dismissal', 'label': 'Незаконное увольнение'},
                    {'value': 'labor_conditions', 'label': 'Нарушение условий труда'},
                    {'value': 'compensation', 'label': 'Возмещение ущерба'},
                    {'value': 'other', 'label': 'Иное'}
                ], 'required': True},
                {'name': 'dispute_circumstances', 'label': 'Обстоятельства нарушения прав', 'type': 'textarea',
                 'required': True},
                {'name': 'dispute_date', 'label': 'Дата нарушения', 'type': 'date', 'required': False},
                {'name': 'violation_amount', 'label': 'Сумма требований (если применимо, руб.)', 'type': 'number',
                 'required': False},
                {'name': 'moral_damage', 'label': 'Сумма морального вреда (руб.)', 'type': 'number', 'required': False}
            ]
        },
        {
            'id': 'evidence',
            'title': 'Доказательства',
            'fields': [
                {'name': 'has_labor_contract', 'label': 'Трудовой договор', 'type': 'checkbox', 'required': False},
                {'name': 'has_employment_order', 'label': 'Приказ о приеме на работу', 'type': 'checkbox',
                 'required': False},
                {'name': 'has_termination_order', 'label': 'Приказ об увольнении', 'type': 'checkbox',
                 'required': False},
                {'name': 'has_salary_evidence', 'label': 'Документы о заработной плате', 'type': 'checkbox',
                 'required': False},
                {'name': 'has_witnesses', 'label': 'Свидетельские показания', 'type': 'checkbox', 'required': False},
                {'name': 'has_pretrial_appeal', 'label': 'Досудебное обращение к работодателю', 'type': 'checkbox',
                 'required': False},
                {'name': 'has_labor_inspection', 'label': 'Обращение в трудовую инспекцию', 'type': 'checkbox',
                 'required': False},
                {'name': 'other_evidence', 'label': 'Иные доказательства', 'type': 'textarea', 'required': False}
            ]
        }
    ]
}


@app.route('/')
def index():
    return render_template('index.html', document_types=DOCUMENT_TYPES)

@app.route('/privacy-policy')
def privacy_policy():
    """
    Страница с политикой конфиденциальности.
    """
    current_date = datetime.datetime.now().strftime("%d.%m.%Y")
    return render_template('privacy_policy.html', current_date=current_date)

@app.route('/clear-data')
def clear_data():
    """
    Очистка данных пользователя из сессии.
    """
    session.clear()
    return redirect(url_for('index'))


@app.route('/questionnaire/<doc_type>', methods=['GET', 'POST'])
def questionnaire(doc_type):
    if doc_type not in DOCUMENT_TYPES:
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Проверка согласия на обработку персональных данных
        if 'data_consent' not in request.form:
            return render_template('questionnaire.html',
                                   doc_type=doc_type,
                                   document=DOCUMENT_TYPES[doc_type],
                                   questions=QUESTIONS[doc_type],
                                   form_data=request.form.to_dict(),
                                   consent_error="Для продолжения необходимо дать согласие на обработку персональных данных")

        # Обработка данных формы
        form_data = request.form.to_dict()

        # Валидация данных
        errors = validate_inputs(form_data, QUESTIONS[doc_type])
        if errors:
            return render_template('questionnaire.html',
                                   doc_type=doc_type,
                                   document=DOCUMENT_TYPES[doc_type],
                                   questions=QUESTIONS[doc_type],
                                   form_data=form_data,
                                   errors=errors)

        # Шифрование данных перед сохранением в сессии
        encrypted_form_data = encrypt_data(form_data, config.SECRET_KEY)
        if encrypted_form_data:
            session['encrypted_form_data'] = encrypted_form_data
        else:
            # Резервное сохранение, если шифрование не удалось
            session['form_data'] = form_data

        session['doc_type'] = doc_type

        # Переход к предпросмотру документа
        return redirect(url_for('preview_document'))

    return render_template('questionnaire.html',
                           doc_type=doc_type,
                           document=DOCUMENT_TYPES[doc_type],
                           questions=QUESTIONS[doc_type],
                           form_data={})


@app.route('/preview', methods=['GET', 'POST'])
def preview_document():
    # Проверка наличия данных в сессии
    if ('encrypted_form_data' not in session and 'form_data' not in session) or 'doc_type' not in session:
        return redirect(url_for('index'))

    # Получение и дешифровка данных
    if 'encrypted_form_data' in session:
        form_data = decrypt_data(session['encrypted_form_data'], config.SECRET_KEY)
        if not form_data:  # Если дешифровка не удалась
            form_data = session.get('form_data', {})
    else:
        form_data = session.get('form_data', {})

    doc_type = session['doc_type']

    # Генерация документа
    document_text = generate_document(doc_type, form_data)

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'enhance':
            # Показываем уведомление о передаче данных
            if 'confirmed_ai_usage' not in session:
                return render_template('ai_confirmation.html',
                                       action='enhance',
                                       doc_type=doc_type,
                                       document=DOCUMENT_TYPES[doc_type])

            # Улучшение документа с помощью ИИ
            enhanced_document = enhance_document(document_text)
            return render_template('document.html',
                                   document_text=enhanced_document,
                                   doc_type=doc_type,
                                   document=DOCUMENT_TYPES[doc_type],
                                   enhanced=True)

        elif action == 'legal_advice':
            # Показываем уведомление о передаче данных
            if 'confirmed_ai_usage' not in session:
                return render_template('ai_confirmation.html',
                                       action='legal_advice',
                                       doc_type=doc_type,
                                       document=DOCUMENT_TYPES[doc_type])

            # Получение юридической консультации от ИИ
            legal_advice = get_legal_advice(document_text)
            return render_template('document.html',
                                   document_text=document_text,
                                   doc_type=doc_type,
                                   document=DOCUMENT_TYPES[doc_type],
                                   legal_advice=legal_advice)

        elif action == 'analyze_strength':
            # Показываем уведомление о передаче данных
            if 'confirmed_ai_usage' not in session:
                return render_template('ai_confirmation.html',
                                       action='analyze_strength',
                                       doc_type=doc_type,
                                       document=DOCUMENT_TYPES[doc_type])

            # Анализ силы юридической позиции
            strength_analysis = analyze_document_strength(document_text)
            return render_template('document.html',
                                   document_text=document_text,
                                   doc_type=doc_type,
                                   document=DOCUMENT_TYPES[doc_type],
                                   strength_analysis=strength_analysis)

        elif action == 'download':
            # Конвертация в PDF и скачивание
            try:
                pdf_bytes = generate_pdf(document_text)
                filename = f"document_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

                return send_file(
                    io.BytesIO(pdf_bytes),
                    mimetype='application/pdf',
                    as_attachment=True,
                    download_name=filename
                )
            except Exception as e:
                print(f"Ошибка генерации PDF: {e}")
                return render_template('document.html',
                                       document_text=document_text,
                                       doc_type=doc_type,
                                       document=DOCUMENT_TYPES[doc_type],
                                       error="Ошибка при создании PDF")

        elif action == 'confirm_ai_usage':
            # Устанавливаем флаг подтверждения использования ИИ
            session['confirmed_ai_usage'] = True
            # Перенаправляем на предыдущее действие
            return redirect(url_for('preview_document', action=request.form.get('original_action')))

    return render_template('document.html',
                           document_text=document_text,
                           doc_type=doc_type,
                           document=DOCUMENT_TYPES[doc_type])


@app.route('/reset')
def reset():
    # Очистка данных сессии
    session.pop('form_data', None)
    session.pop('doc_type', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=config.DEBUG)

@app.teardown_appcontext
def teardown_db(exception):
    """
    Очистка сессии при завершении работы с приложением.
    """
    # Можно добавить логику очистки данных здесь, если требуется
    pass







