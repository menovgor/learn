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


document.addEventListener('DOMContentLoaded', function() {
    // Включаем всплывающие подсказки
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Валидация полей формы
    const form = document.getElementById('questionnaireForm');
    if (form) {
        // Функция для проверки ИНН
        function validateINN(inn) {
            // Разные правила для ИНН физлиц (12 цифр) и организаций (10 цифр)
            if (!inn.match(/^\d+$/)) return false;
            if (inn.length === 10) {
                // Для юридических лиц
                let checkDigit = calculateCheckDigit(inn, [2, 4, 10, 3, 5, 9, 4, 6, 8]);
                return inn[9] == checkDigit;
            } else if (inn.length === 12) {
                // Для физических лиц
                let checkDigit1 = calculateCheckDigit(inn, [7, 2, 4, 10, 3, 5, 9, 4, 6, 8]);
                let checkDigit2 = calculateCheckDigit(inn, [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8]);
                return inn[10] == checkDigit1 && inn[11] == checkDigit2;
            }
            return false;
        }

        function calculateCheckDigit(inn, coefficients) {
            let sum = 0;
            for (let i = 0; i < coefficients.length; i++) {
                sum += coefficients[i] * inn[i];
            }
            return (sum % 11) % 10;
        }

        // Функция для проверки ОГРН/ОГРНИП
        function validateOGRN(ogrn) {
            if (!ogrn.match(/^\d+$/)) return false;
            if (ogrn.length === 13) {
                // Для юридических лиц
                let checkDigit = (parseInt(ogrn.slice(0, -1)) % 11) % 10;
                return ogrn[12] == checkDigit;
            } else if (ogrn.length === 15) {
                // Для ИП
                let checkDigit = (parseInt(ogrn.slice(0, -1)) % 13) % 10;
                return ogrn[14] == checkDigit;
            }
            return false;
        }

        // Валидация поля в зависимости от его типа
        function validateField(field) {
            let isValid = true;
            let errorMessage = '';

            // Если поле обязательное, проверяем его заполнение
            if (field.required && !field.value.trim()) {
                isValid = false;
                errorMessage = 'Это поле обязательно для заполнения';
            } else if (field.value.trim()) {
                // Проверяем разные типы полей
                switch(field.id) {
                    case 'plaintiff_inn':
                    case 'defendant_inn':
                        if (!validateINN(field.value)) {
                            isValid = false;
                            errorMessage = 'Неверный формат ИНН. Должно быть 10 цифр для организаций или 12 цифр для физлиц.';
                        }
                        break;
                    case 'plaintiff_ogrn':
                    case 'defendant_ogrn':
                        if (!validateOGRN(field.value)) {
                            isValid = false;
                            errorMessage = 'Неверный формат ОГРН/ОГРНИП. Должно быть 13 цифр для организаций или 15 цифр для ИП.';
                        }
                        break;
                    case 'plaintiff_phone':
                        if (!field.value.match(/^(\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}$/)) {
                            isValid = false;
                            errorMessage = 'Неверный формат телефона. Пример: +7 (999) 123-45-67';
                        }
                        break;
                    case 'plaintiff_email':
                        if (field.value && !field.value.match(/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/)) {
                            isValid = false;
                            errorMessage = 'Неверный формат email.';
                        }
                        break;
                    case 'debt_amount':
                        if (isNaN(parseFloat(field.value)) || parseFloat(field.value) <= 0) {
                            isValid = false;
                            errorMessage = 'Сумма долга должна быть положительным числом.';
                        }
                        break;
                }
            }

            // Показываем или скрываем сообщение об ошибке
            const fieldContainer = field.closest('.form-group');

            if (!isValid) {
                field.classList.add('is-invalid');
                field.classList.remove('is-valid');

                // Создаем или обновляем сообщение об ошибке
                let feedbackElement = fieldContainer.querySelector('.invalid-feedback');
                if (!feedbackElement) {
                    feedbackElement = document.createElement('div');
                    feedbackElement.className = 'invalid-feedback';
                    field.insertAdjacentElement('afterend', feedbackElement);
                }
                feedbackElement.textContent = errorMessage;
            } else {
                field.classList.remove('is-invalid');
                field.classList.add('is-valid');

                // Удаляем сообщение об ошибке, если оно есть
                const feedbackElement = fieldContainer.querySelector('.invalid-feedback');
                if (feedbackElement) {
                    feedbackElement.remove();
                }
            }

            return isValid;
        }

        // Добавляем обработчики для всех полей
        const formFields = form.querySelectorAll('input, select, textarea');
        formFields.forEach(field => {
            // Валидация при потере фокуса
            field.addEventListener('blur', function() {
                validateField(this);
            });

            // Валидация при изменении значения (для выпадающих списков и чекбоксов)
            if (field.tagName === 'SELECT' || field.type === 'checkbox' || field.type === 'radio') {
                field.addEventListener('change', function() {
                    validateField(this);
                });
            }
        });

        // Валидация формы перед отправкой
        form.addEventListener('submit', function(e) {
            let isFormValid = true;

            // Проверяем все поля
            formFields.forEach(field => {
                if (!validateField(field)) {
                    isFormValid = false;
                }
            });

            // Проверяем зависимые поля (например, сумма неустойки не может быть больше суммы долга)
            const debtAmount = parseFloat(document.getElementById('debt_amount')?.value || 0);
            const penaltyAmount = parseFloat(document.getElementById('penalty_amount')?.value || 0);

            if (penaltyAmount > debtAmount) {
                const penaltyField = document.getElementById('penalty_amount');
                penaltyField.classList.add('is-invalid');

                const fieldContainer = penaltyField.closest('.form-group');
                let feedbackElement = fieldContainer.querySelector('.invalid-feedback');
                if (!feedbackElement) {
                    feedbackElement = document.createElement('div');
                    feedbackElement.className = 'invalid-feedback';
                    penaltyField.insertAdjacentElement('afterend', feedbackElement);
                }
                feedbackElement.textContent = 'Сумма неустойки не может превышать сумму основного долга.';

                isFormValid = false;
            }

            if (!isFormValid) {
                e.preventDefault();
                // Прокручиваем к первому полю с ошибкой
                const firstInvalidField = form.querySelector('.is-invalid');
                if (firstInvalidField) {
                    firstInvalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    firstInvalidField.focus();
                }
            }
        });

        // Зависимые поля (показывать/скрывать в зависимости от значений других полей)
        const dependentFields = form.querySelectorAll('[data-dependent]');

        function updateDependentFields() {
            dependentFields.forEach(field => {
                const dependencyInfo = field.getAttribute('data-dependent').split(':');
                if (dependencyInfo.length === 2) {
                    const [dependsOn, valueToShow] = dependencyInfo;
                    const masterField = document.getElementById(dependsOn);

                    if (masterField) {
                        const masterValue = masterField.type === 'checkbox' ? masterField.checked : masterField.value;
                        const fieldRow = field.closest('.col-md-6, .col-md-12');

                        if (masterValue == valueToShow) {
                            fieldRow.style.display = 'block';
                            // Проверяем, нужно ли сделать поле обязательным
                            if (field.hasAttribute('data-required-if-shown')) {
                                field.required = true;
                                const label = field.closest('.form-group').querySelector('label');
                                if (label && !label.querySelector('.text-danger')) {
                                    label.innerHTML += '<span class="text-danger">*</span>';
                                }
                            }
                        } else {
                            fieldRow.style.display = 'none';
                            // Снимаем обязательность при скрытии
                            field.required = false;
                        }
                    }
                }
            });
        }

        // Добавляем обработчики для полей, от которых зависят другие поля
        const masterFields = new Set();
        dependentFields.forEach(field => {
            const dependencyInfo = field.getAttribute('data-dependent').split(':');
            if (dependencyInfo.length === 2) {
                masterFields.add(dependencyInfo[0]);
            }
        });

        masterFields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                field.addEventListener('change', updateDependentFields);
            }
        });

        // Инициализация зависимых полей при загрузке страницы
        updateDependentFields();
    }

    // Функция для заполнения примера текста
    window.fillExampleText = function(fieldId, exampleText) {
        const field = document.getElementById(fieldId);
        if (field) {
            field.value = exampleText;
            // Валидируем поле после заполнения
            const event = new Event('blur');
            field.dispatchEvent(event);
        }
    };
});