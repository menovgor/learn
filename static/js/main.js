// Инициализация всех всплывающих подсказок
document.addEventListener('DOMContentLoaded', function() {
    // Инициализация всплывающих подсказок Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Добавление подсветки для полей при фокусе
    const formFields = document.querySelectorAll('.form-control, .form-select');
    formFields.forEach(field => {
        field.addEventListener('focus', function() {
            this.closest('.form-group').classList.add('focused');
        });

        field.addEventListener('blur', function() {
            this.closest('.form-group').classList.remove('focused');
        });
    });

    // Обработчик для условного отображения полей в зависимости от выбранных значений
    const conditionalFields = document.querySelectorAll('[data-condition-field]');
    const triggerFields = document.querySelectorAll('[id^="plaintiff_type"], [id^="defendant_type"], [id^="court_type"]');

    function updateConditionalFields() {
        conditionalFields.forEach(field => {
            const conditionField = field.getAttribute('data-condition-field');
            const conditionValue = field.getAttribute('data-condition-value');
            const conditionElement = document.getElementById(conditionField);

            if (conditionElement && conditionElement.value === conditionValue) {
                field.closest('.col-md-6, .col-md-12').style.display = 'block';
            } else {
                field.closest('.col-md-6, .col-md-12').style.display = 'none';
            }
        });
    }

    triggerFields.forEach(field => {
        field.addEventListener('change', updateConditionalFields);
    });

    // Вызываем функцию при загрузке страницы
    updateConditionalFields();

    // Обработчик для расчета суммы иска и госпошлины
    const debtAmountField = document.getElementById('debt_amount');
    const penaltyAmountField = document.getElementById('penalty_amount');
    const totalSumField = document.getElementById('total_sum');
    const courtFeeField = document.getElementById('court_fee');

    function calculateTotal() {
        if (debtAmountField && penaltyAmountField && totalSumField) {
            const debtAmount = parseFloat(debtAmountField.value) || 0;
            const penaltyAmount = parseFloat(penaltyAmountField.value) || 0;
            const totalSum = debtAmount + penaltyAmount;

            if (totalSumField) {
                totalSumField.value = totalSum.toFixed(2);
            }

            // Расчет госпошлины по формуле (упрощенно)
            if (courtFeeField) {
                let courtFee = 0;

                if (totalSum <= 20000) {
                    courtFee = Math.max(totalSum * 0.04, 400);
                } else if (totalSum <= 100000) {
                    courtFee = 800 + (totalSum - 20000) * 0.03;
                } else if (totalSum <= 200000) {
                    courtFee = 3200 + (totalSum - 100000) * 0.02;
                } else if (totalSum <= 1000000) {
                    courtFee = 5200 + (totalSum - 200000) * 0.01;
                } else {
                    courtFee = 13200 + (totalSum - 1000000) * 0.005;
                }

                courtFeeField.value = Math.ceil(courtFee);
            }
        }
    }

    if (debtAmountField) {
        debtAmountField.addEventListener('input', calculateTotal);
    }

    if (penaltyAmountField) {
        penaltyAmountField.addEventListener('input', calculateTotal);
    }

    // Вызываем функцию расчета при загрузке страницы
    calculateTotal();

    // Обработчик для предпросмотра документа
    const previewBtn = document.getElementById('previewBtn');
    const documentForm = document.getElementById('questionnaireForm');

    if (previewBtn && documentForm) {
        previewBtn.addEventListener('click', function(e) {
            e.preventDefault();

            // Проверка валидности формы
            if (!documentForm.checkValidity()) {
                documentForm.reportValidity();
                return;
            }

            // Показываем индикатор загрузки
            const originalText = previewBtn.innerHTML;
            previewBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Генерация...';
            previewBtn.disabled = true;

            // Отправляем форму
            documentForm.submit();
        });
    }
});

// Функция для копирования текста документа в буфер обмена
function copyToClipboard() {
    const documentText = document.querySelector('.document-preview pre').innerText;

    navigator.clipboard.writeText(documentText).then(
        function() {
            // Создаем временное уведомление
            const alert = document.createElement('div');
            alert.className = 'alert alert-success alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3';
            alert.style.zIndex = '9999';
            alert.innerHTML = `
                <i class="bi bi-check-circle-fill me-2"></i> Документ скопирован в буфер обмена
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;

            document.body.appendChild(alert);

            // Автоматическое скрытие через 3 секунды
            setTimeout(function() {
                alert.remove();
            }, 3000);
        },
        function(err) {
            console.error('Ошибка при копировании: ', err);
        }
    );
}

// Функция для сравнения оригинального и улучшенного документов
function compareDocuments() {
    // Получаем содержимое модального окна
    const modalBody = document.querySelector('#compareModal .modal-body');

    // Получаем тексты документов
    const originalText = document.getElementById('originalDocText').value;
    const enhancedText = document.querySelector('.document-preview pre').innerText;

    // Разбиваем тексты на строки
    const originalLines = originalText.split('\n');
    const enhancedLines = enhancedText.split('\n');

    // Создаем HTML для сравнения
    let comparisonHtml = '<div class="row"><div class="col-md-6"><h6 class="text-muted">Оригинальный документ</h6><pre class="bg-light p-3">';

    for (let i = 0; i < originalLines.length; i++) {
        if (i < enhancedLines.length && originalLines[i] !== enhancedLines[i]) {
            comparisonHtml += `<span class="bg-warning bg-opacity-25">${originalLines[i]}</span>\n`;
        } else {
            comparisonHtml += originalLines[i] + '\n';
        }
    }

    comparisonHtml += '</pre></div><div class="col-md-6"><h6 class="text-muted">Улучшенный документ</h6><pre class="bg-light p-3">';

    for (let i = 0; i < enhancedLines.length; i++) {
        if (i < originalLines.length && originalLines[i] !== enhancedLines[i]) {
            comparisonHtml += `<span class="bg-success bg-opacity-25">${enhancedLines[i]}</span>\n`;
        } else {
            comparisonHtml += enhancedLines[i] + '\n';
        }
    }

    comparisonHtml += '</pre></div></div>';

    // Вставляем HTML в модальное окно
    modalBody.innerHTML = comparisonHtml;
}

// Функция для управления видимостью полей в зависимости от типа лица
function updateFieldsByPersonType() {
    const plaintiffTypeSelect = document.getElementById('plaintiff_type');
    if (!plaintiffTypeSelect) return;

    const innField = document.getElementById('plaintiff_inn');
    const ogrnField = document.getElementById('plaintiff_ogrn');

    if (!innField || !ogrnField) return;

    const innContainer = innField.closest('.col-md-6');
    const ogrnContainer = ogrnField.closest('.col-md-6');

    // При изменении типа лица
    plaintiffTypeSelect.addEventListener('change', function() {
        const isIndividual = this.value === 'individual';

        // Управление обязательностью
        innField.required = !isIndividual;
        ogrnField.required = !isIndividual;

        // Управление маркировкой (звездочкой)
        const innLabel = innContainer.querySelector('label');
        const ogrnLabel = ogrnContainer.querySelector('label');

        if (innLabel) {
            innLabel.innerHTML = isIndividual ?
                'ИНН' :
                'ИНН <span class="text-danger">*</span>';
        }

        if (ogrnLabel) {
            ogrnLabel.innerHTML = isIndividual ?
                'ОГРН/ОГРНИП' :
                'ОГРН/ОГРНИП <span class="text-danger">*</span>';
        }
    });

    // Вызываем функцию при загрузке страницы
    plaintiffTypeSelect.dispatchEvent(new Event('change'));
}

// Вызов функции при загрузке документа
document.addEventListener('DOMContentLoaded', function() {
    updateFieldsByPersonType();
    // Другие существующие вызовы...
});