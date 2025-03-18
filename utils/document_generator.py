import os
import re
import datetime
import num2words
import config
from string import Template


def load_template(doc_type):
    """
    Загружает шаблон документа из файла.
    """
    template_path = os.path.join(config.DOCUMENT_TEMPLATES_DIR, f"{doc_type}.txt")
    try:
        with open(template_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        # Если файл не найден, используем резервный базовый шаблон
        return get_fallback_template(doc_type)


def get_fallback_template(doc_type):
    """
    Создает резервный шаблон, если файл шаблона отсутствует.
    """
    if doc_type == 'debt_collection':
        return """
                                В $court_name
                                $court_address

                Истец: $plaintiff_name
                Адрес: $plaintiff_address
                ИНН: $plaintiff_inn
                $plaintiff_ogrn_label: $plaintiff_ogrn
                Телефон: $plaintiff_phone
                $plaintiff_email_block

                Ответчик: $defendant_name
                Адрес: $defendant_address
                $defendant_inn_block
                $defendant_ogrn_block

                ИСКОВОЕ ЗАЯВЛЕНИЕ
                о взыскании задолженности

                $claim_date между Истцом и Ответчиком был заключен договор №$contract_number (далее – Договор), согласно которому $contract_subject.

                В соответствии с условиями Договора, Истец исполнил свои обязательства в полном объеме, что подтверждается следующими документами: $execution_confirmation.

                Согласно пункту ___ Договора, Ответчик обязан был $defendant_obligation в срок до ___, однако свои обязательства не исполнил (исполнил ненадлежащим образом).

                $claim_circumstances

                По состоянию на $current_date размер задолженности Ответчика составляет $debt_amount_str ($debt_amount_words) рублей.

                $penalty_block

                $interest_block

                В соответствии со статьями 309, 310 Гражданского кодекса РФ обязательства должны исполняться надлежащим образом, а односторонний отказ от исполнения обязательства не допускается.

                $pretension_block

                На основании изложенного, руководствуясь статьями 309, 310, $additional_articles Гражданского кодекса РФ, статьями 131, 132 Гражданского процессуального кодекса РФ (Арбитражного процессуального кодекса РФ),

                ПРОШУ:

                1. Взыскать с Ответчика $defendant_name в пользу Истца $plaintiff_name сумму основного долга в размере $debt_amount_str ($debt_amount_words) рублей.

                $penalty_claim

                $interest_claim

                $costs_claim

                Приложения:
                1. Копия договора № $contract_number от $claim_date.
                2. Документы, подтверждающие исполнение обязательств Истцом.
                3. Расчет исковых требований.
                4. Документ об оплате государственной пошлины.
                $additional_attachments

                Истец / Представитель Истца:
                _________________ / $plaintiff_short_name /

                $current_full_date
                """
    else:
        # Базовый шаблон для других типов документов
        return """
                                Документ: $document_name

                Данный шаблон является временным и требует настройки.

                $doc_data

                Дата: $current_full_date

                Подпись: _______________
                """





def format_date(date_str):
    """
    Форматирует дату из строкового представления в формат ДД.ММ.ГГГГ.
    """
    try:
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%d.%m.%Y')
    except ValueError:
        return date_str


def num_to_words(amount):
    """
    Преобразует число в строковое представление прописью.
    """
    try:
        amount_float = float(amount)
        return num2words.num2words(amount_float, lang='ru')
    except:
        return str(amount)


def generate_document(doc_type, form_data):
    """
    Генерирует текст документа на основе шаблона и заполненных данных.
    """
    template = load_template(doc_type)

    # Создаем словарь для подстановки значений
    data = {}

    # Добавляем все поля из формы в словарь
    for key, value in form_data.items():
        data[key] = value

    # Текущая дата
    current_date = datetime.datetime.now()
    data['current_date'] = current_date.strftime('%d.%m.%Y')
    data['current_full_date'] = f"{current_date.strftime('%d.%m.%Y')} г."

    # Форматирование дат
    if 'contract_date' in form_data:
        data['claim_date'] = format_date(form_data['contract_date'])

    # Специфические для типа документа преобразования
    if doc_type == 'debt_collection':
        # Конвертация суммы долга в слова
        if 'debt_amount' in form_data and form_data['debt_amount']:
            debt_amount = form_data['debt_amount']
            data['debt_amount_str'] = "{:,.2f}".format(float(debt_amount)).replace(',', ' ')
            data['debt_amount_words'] = num_to_words(debt_amount)

        # Определение типа истца/ответчика
        if form_data.get('plaintiff_type') == 'legal':
            data['plaintiff_ogrn_label'] = 'ОГРН'
        else:
            data['plaintiff_ogrn_label'] = 'ОГРНИП'

        # Email блок
        if 'plaintiff_email' in form_data and form_data['plaintiff_email']:
            data['plaintiff_email_block'] = f"Email: {form_data['plaintiff_email']}"
        else:
            data['plaintiff_email_block'] = ""

        # ИНН/ОГРН блоки ответчика
        if 'defendant_inn' in form_data and form_data['defendant_inn']:
            data['defendant_inn_block'] = f"ИНН: {form_data['defendant_inn']}"
        else:
            data['defendant_inn_block'] = ""

        if 'defendant_ogrn' in form_data and form_data['defendant_ogrn']:
            data['defendant_ogrn_block'] = f"ОГРН/ОГРНИП: {form_data['defendant_ogrn']}"
        else:
            data['defendant_ogrn_block'] = ""

        # Блоки о неустойке и процентах
        if 'penalty_amount' in form_data and form_data['penalty_amount'] and float(form_data['penalty_amount']) > 0:
            penalty_amount = float(form_data['penalty_amount'])
            data[
                'penalty_block'] = f"Также в соответствии с пунктом ___ Договора за нарушение сроков оплаты предусмотрена неустойка в размере {penalty_amount:,.2f} ({num_to_words(penalty_amount)}) рублей."
            data[
                'penalty_claim'] = f"2. Взыскать с Ответчика {form_data.get('defendant_name')} в пользу Истца {form_data.get('plaintiff_name')} неустойку в размере {penalty_amount:,.2f} ({num_to_words(penalty_amount)}) рублей."
        else:
            data['penalty_block'] = ""
            data['penalty_claim'] = ""

        if 'interest_rate' in form_data and form_data['interest_rate'] and float(form_data['interest_rate']) > 0:
            interest_rate = form_data['interest_rate']
            data[
                'interest_block'] = f"Кроме того, в соответствии со ст. 395 ГК РФ за пользование чужими денежными средствами подлежат начислению проценты по ключевой ставке Банка России в размере {interest_rate}%."
            data[
                'interest_claim'] = f"3. Взыскать с Ответчика {form_data.get('defendant_name')} в пользу Истца {form_data.get('plaintiff_name')} проценты за пользование чужими денежными средствами, начисленные на сумму долга."
        else:
            data['interest_block'] = ""
            data['interest_claim'] = ""

        # Блок о претензии
        if 'has_pretension' in form_data and form_data['has_pretension'] == 'yes':
            data[
                'pretension_block'] = "В адрес Ответчика была направлена претензия с требованием оплатить задолженность, однако до настоящего времени оплата не произведена, ответ на претензию не получен."
        else:
            data['pretension_block'] = ""

        # Дополнительные статьи ГК РФ
        data['additional_articles'] = "317, 395"

        # Истец сокращенно
        if 'plaintiff_name' in form_data:
            plaintiff_name = form_data['plaintiff_name']
            name_parts = plaintiff_name.split()
            if len(name_parts) >= 3 and form_data.get('plaintiff_type') == 'individual':
                data['plaintiff_short_name'] = f"{name_parts[0]} {name_parts[1][0]}.{name_parts[2][0]}."
            else:
                data['plaintiff_short_name'] = plaintiff_name

        # Судебные расходы
        data[
            'costs_claim'] = f"4. Взыскать с Ответчика в пользу Истца расходы по уплате государственной пошлины в размере ___ рублей."

        # Дополнительные приложения
        additional_attachments = []
        if 'has_pretension' in form_data and form_data['has_pretension'] == 'yes':
            additional_attachments.append("5. Копия претензии и доказательства ее направления.")

        if 'has_correspondence' in form_data and form_data['has_correspondence'] == 'yes':
            additional_attachments.append(f"{5 + len(additional_attachments)}. Копии переписки сторон.")

        if 'other_attachments' in form_data and form_data['other_attachments']:
            attachments = form_data['other_attachments'].split('\n')
            for attachment in attachments:
                if attachment.strip():
                    additional_attachments.append(f"{5 + len(additional_attachments)}. {attachment.strip()}.")

        if additional_attachments:
            data['additional_attachments'] = '\n'.join(additional_attachments)
        else:
            data['additional_attachments'] = ""

        # Описание предмета договора и обязательств ответчика
        data[
            'contract_subject'] = "Истец обязался выполнить [описание работ/услуг/поставки товара], а Ответчик обязался принять и оплатить их"
        data['defendant_obligation'] = "оплатить [работы/услуги/товар] в размере [сумма] рублей"
        data['execution_confirmation'] = "[перечень документов, подтверждающих исполнение]"



    elif doc_type == 'labor_dispute':
        # Форматирование дат
        for date_field in ['employment_start_date', 'employment_end_date', 'contract_date', 'dispute_date']:
            if date_field in form_data and form_data[date_field]:
                data[date_field] = format_date(form_data[date_field])

        # Обработка типа спора
        dispute_type_map = {
            'unpaid_salary': 'взыскании невыплаченной заработной платы',
            'illegal_dismissal': 'восстановлении на работе и оплате вынужденного прогула',
            'labor_conditions': 'нарушении условий труда',
            'compensation': 'возмещении ущерба',
            'other': 'защите трудовых прав'
        }

        if 'dispute_type' in form_data:
            dispute_type_key = form_data['dispute_type']
            data['dispute_type'] = dispute_type_map.get(dispute_type_key, 'защите трудовых прав')

        # Определение статей ТК РФ в зависимости от типа спора
        labor_code_articles_map = {
            'unpaid_salary': '136, 140, 236, 237, 391, 392, 419',
            'illegal_dismissal': '77, 81, 83, 84, 394, 396, 419',
            'labor_conditions': '21, 22, 161, 163, 219, 419',
            'compensation': '232, 233, 234, 237, 238, 419',
            'other': '21, 22, 419'
        }

        if 'dispute_type' in form_data:
            dispute_type_key = form_data['dispute_type']
            data['labor_code_articles'] = labor_code_articles_map.get(dispute_type_key, '21, 22, 419')

        # Формирование юридического обоснования
        legal_basis_map = {
            'unpaid_salary': 'работодатель обязан выплачивать заработную плату не реже чем каждые полмесяца, а при прекращении трудового договора выплата всех сумм, причитающихся работнику, производится в день увольнения.',
            'illegal_dismissal': 'при незаконном увольнении работник подлежит восстановлению на прежней работе, а также ему выплачивается средний заработок за время вынужденного прогула.',
            'labor_conditions': 'работодатель обязан обеспечивать безопасность и условия труда, соответствующие государственным нормативным требованиям охраны труда.',
            'compensation': 'работодатель обязан возместить работнику материальный ущерб, причиненный в результате незаконного лишения его возможности трудиться.',
            'other': 'работодатель обязан соблюдать трудовое законодательство и иные нормативные правовые акты, содержащие нормы трудового права.'
        }

        if 'dispute_type' in form_data:
            dispute_type_key = form_data['dispute_type']
            data['legal_basis'] = legal_basis_map.get(dispute_type_key,
                                                      'работодатель обязан соблюдать права работников, предусмотренные трудовым законодательством.')

        # Применимая статья ТК РФ для нарушения
        labor_code_article_map = {
            'unpaid_salary': '136',
            'illegal_dismissal': '394',
            'labor_conditions': '219',
            'compensation': '234',
            'other': '21'
        }

        if 'dispute_type' in form_data:
            dispute_type_key = form_data['dispute_type']
            data['labor_code_article'] = labor_code_article_map.get(dispute_type_key, '21')

        # Формирование требований
        primary_demand_map = {
            'unpaid_salary': f"Взыскать с {form_data.get('defendant_name')} в мою пользу невыплаченную заработную плату в размере {form_data.get('violation_amount', '___')} рублей.",
            'illegal_dismissal': f"Признать приказ об увольнении №___ от ___ незаконным, восстановить меня, {form_data.get('plaintiff_name')}, в должности {form_data.get('position')}.",
            'labor_conditions': f"Обязать {form_data.get('defendant_name')} устранить нарушения трудового законодательства в части обеспечения надлежащих условий труда.",
            'compensation': f"Взыскать с {form_data.get('defendant_name')} в мою пользу возмещение материального ущерба в размере {form_data.get('violation_amount', '___')} рублей.",
            'other': f"Признать действия (бездействие) {form_data.get('defendant_name')} нарушающими мои трудовые права и обязать устранить данное нарушение."
        }

        if 'dispute_type' in form_data:
            dispute_type_key = form_data['dispute_type']
            data['primary_demand'] = primary_demand_map.get(dispute_type_key,
                                                            f"Признать действия {form_data.get('defendant_name')} нарушающими мои трудовые права и обязать устранить данное нарушение.")

        # Дополнительные требования
        additional_demands = []

        if 'dispute_type' in form_data and form_data['dispute_type'] == 'illegal_dismissal':
            additional_demands.append(
                f"2. Взыскать с {form_data.get('defendant_name')} в мою пользу средний заработок за время вынужденного прогула с ___ по ___ в размере ___ рублей.")

        if 'dispute_type' in form_data and form_data['dispute_type'] == 'unpaid_salary':
            additional_demands.append(
                f"2. Взыскать с {form_data.get('defendant_name')} в мою пользу проценты за задержку выплаты заработной платы в соответствии со ст. 236 ТК РФ в размере ___ рублей.")

        if 'dispute_type' in form_data and form_data['dispute_type'] == 'labor_conditions':
            additional_demands.append(
                f"2. Обязать {form_data.get('defendant_name')} провести специальную оценку условий труда на моем рабочем месте.")

        # Формирование строки для требования о компенсации морального вреда
        if 'moral_damage' in form_data and form_data['moral_damage'] and float(form_data['moral_damage']) > 0:
            moral_damage_amount = float(form_data['moral_damage'])
            additional_demands_count = len(
                additional_demands) + 2  # +1 за основное требование, +1 за текущее о моральном вреде
            data[
                'compensation_demand'] = f"{additional_demands_count}. Взыскать с {form_data.get('defendant_name')} в мою пользу компенсацию морального вреда в размере {moral_damage_amount:,.2f} ({num_to_words(moral_damage_amount)}) рублей."
        else:
            data['compensation_demand'] = ""

        # Формирование строки для требования о судебных расходах
        additional_demands_count = len(
            additional_demands) + 2  # +1 за основное требование, +1 за моральный вред (если есть)
        if 'moral_damage' not in form_data or not form_data['moral_damage']:
            additional_demands_count -= 1  # если нет морального вреда

        data[
            'legal_costs_demand'] = f"{additional_demands_count}. Взыскать с {form_data.get('defendant_name')} в мою пользу расходы по уплате государственной пошлины в размере ___ рублей."

        # Формирование строки дополнительных требований
        if additional_demands:
            data['additional_demands'] = "\n".join(additional_demands)
        else:
            data['additional_demands'] = ""

        # Формирование строки с информацией о досудебном урегулировании
        if 'has_pretrial_appeal' in form_data and form_data['has_pretrial_appeal'] == 'yes':
            data[
                'pretrial_settlement'] = f"В целях досудебного урегулирования спора мной было направлено обращение ответчику от ___ с требованием ___, однако ответчик оставил мои требования без удовлетворения (не ответил на обращение)."
        else:
            data[
                'pretrial_settlement'] = "В силу статьи 392 Трудового кодекса РФ досудебный порядок урегулирования трудовых споров не является обязательным."

        # Формирование списка приложений
        termination_order = ""
        if 'has_termination_order' in form_data and form_data['has_termination_order'] == 'yes':
            termination_order = "3. Копия приказа об увольнении."
        data['termination_order'] = termination_order

        salary_evidence = ""
        if 'has_salary_evidence' in form_data and form_data['has_salary_evidence'] == 'yes':
            if termination_order:
                salary_evidence = "4. Справка о заработной плате и иные документы о начислениях."
            else:
                salary_evidence = "3. Справка о заработной плате и иные документы о начислениях."
        data['salary_evidence'] = salary_evidence

        pretrial_documents = ""
        if 'has_pretrial_appeal' in form_data and form_data['has_pretrial_appeal'] == 'yes':
            pretrial_idx = 3
            if termination_order:
                pretrial_idx += 1
            if salary_evidence:
                pretrial_idx += 1
            pretrial_documents = f"{pretrial_idx}. Копия обращения к работодателю и доказательство его направления."

        if 'has_labor_inspection' in form_data and form_data['has_labor_inspection'] == 'yes':
            labor_idx = 3
            if termination_order:
                labor_idx += 1
            if salary_evidence:
                labor_idx += 1
            if pretrial_documents:
                labor_idx += 1
            if pretrial_documents:
                pretrial_documents += f"\n{labor_idx}. Копия обращения в трудовую инспекцию и ответ на него."
            else:
                pretrial_documents = f"{labor_idx}. Копия обращения в трудовую инспекцию и ответ на него."

        data['pretrial_documents'] = pretrial_documents

        witness_statements = ""
        if 'has_witnesses' in form_data and form_data['has_witnesses'] == 'yes':
            witness_idx = 3
            if termination_order:
                witness_idx += 1
            if salary_evidence:
                witness_idx += 1
            if pretrial_documents:
                witness_idx += 1
                if 'has_labor_inspection' in form_data and form_data['has_labor_inspection'] == 'yes':
                    witness_idx += 1
            witness_statements = f"{witness_idx}. Письменные показания свидетелей."
        data['witness_statements'] = witness_statements

        # Прочие доказательства
        other_attachments = ""
        if 'other_evidence' in form_data and form_data['other_evidence']:
            other_idx = 3
            if termination_order:
                other_idx += 1
            if salary_evidence:
                other_idx += 1
            if pretrial_documents:
                other_idx += 1
                if 'has_labor_inspection' in form_data and form_data['has_labor_inspection'] == 'yes':
                    other_idx += 1
            if witness_statements:
                other_idx += 1

            other_evidence_list = []
            attachments = form_data['other_evidence'].split('\n')
            for attachment in attachments:
                if attachment.strip():
                    other_evidence_list.append(f"{other_idx}. {attachment.strip()}.")
                    other_idx += 1

            if other_evidence_list:
                other_attachments = '\n'.join(other_evidence_list)
        data['other_attachments'] = other_attachments

        # Формирование уведомления о копиях
        data['copies_statement'] = f"6. Копия искового заявления и приложений для ответчика."

        # Истец сокращенно (ФИО)
        if 'plaintiff_name' in form_data:
            plaintiff_name = form_data['plaintiff_name']
            name_parts = plaintiff_name.split()
            if len(name_parts) >= 3:
                data['plaintiff_short_name'] = f"{name_parts[0]} {name_parts[1][0]}.{name_parts[2][0]}."
            else:
                data['plaintiff_short_name'] = plaintiff_name

    # Заполняем все неопределенные переменные шаблона пустыми строками
    template_vars = re.findall(r'\$([a-zA-Z_]+)', template)
    for var in template_vars:
        if var not in data:
            data[var] = ""

    # Создаем объект шаблона и подставляем значения
    template_obj = Template(template)
    return template_obj.safe_substitute(data)


def generate_pdf(document_text):
    """
    Генерирует PDF документ из текста используя ReportLab.
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
    from io import BytesIO

    # Создаем буфер для PDF
    buffer = BytesIO()

    # Создаем документ
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=72)

    # Регистрируем шрифт Times New Roman (если возможно)
    try:
        pdfmetrics.registerFont(TTFont('TimesNewRoman', 'C:\\Windows\\Fonts\\times.ttf'))
        font_name = 'TimesNewRoman'
    except:
        # Если не удалось подключить Times, используем стандартный шрифт
        font_name = 'Times-Roman'

    # Создаем стиль для текста документа
    styles = getSampleStyleSheet()
    normal_style = ParagraphStyle(
        'Normal',
        fontName=font_name,
        fontSize=12,
        leading=14,
        alignment=TA_LEFT
    )

    # Разбиваем текст документа на строки и заменяем спецсимволы
    lines = document_text.split('\n')

    # Создаем элементы для документа
    elements = []
    for line in lines:
        if line.strip():
            # Заменяем спецсимволы HTML-эквивалентами
            line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            p = Paragraph(line, normal_style)
            elements.append(p)
        else:
            elements.append(Spacer(1, 12))

    # Строим документ
    doc.build(elements)

    # Получаем содержимое PDF
    pdf_value = buffer.getvalue()
    buffer.close()

    return pdf_value