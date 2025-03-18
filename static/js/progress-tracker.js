document.addEventListener('DOMContentLoaded', function() {
  // Управление шагами
  setupProgressTracker();
});

function setupProgressTracker() {
  // Получаем кнопки навигации
  const sections = document.querySelectorAll('.section-card');
  if (sections.length === 0) return;

  // Создаем кнопки "Далее" и "Назад" для каждой секции
  sections.forEach((section, index) => {
    const footer = section.querySelector('.card-body').appendChild(document.createElement('div'));
    footer.className = 'd-flex justify-content-between mt-4';

    // Кнопка "Назад"
    if (index > 0) {
      const backBtn = document.createElement('button');
      backBtn.type = 'button';
      backBtn.className = 'btn btn-outline-secondary';
      backBtn.innerHTML = '<i class="bi bi-arrow-left"></i> Назад';
      backBtn.addEventListener('click', () => goToStep(index));
      footer.appendChild(backBtn);
    } else {
      const backLink = document.createElement('a');
      backLink.href = "/";
      backLink.className = 'btn btn-outline-secondary';
      backLink.innerHTML = '<i class="bi bi-arrow-left"></i> Назад';
      footer.appendChild(backLink);
    }

    // Кнопка "Далее"
    if (index < sections.length - 1) {
      const nextBtn = document.createElement('button');
      nextBtn.type = 'button';
      nextBtn.className = 'btn btn-primary';
      nextBtn.innerHTML = 'Далее <i class="bi bi-arrow-right"></i>';
      nextBtn.addEventListener('click', () => validateAndGoToStep(index + 2));
      footer.appendChild(nextBtn);
    } else {
      const submitBtn = document.createElement('button');
      submitBtn.type = 'submit';
      submitBtn.className = 'btn btn-success';
      submitBtn.innerHTML = 'Сформировать документ <i class="bi bi-file-earmark-text"></i>';
      footer.appendChild(submitBtn);
    }
  });

  // Удаляем оригинальные кнопки (если они есть)
  const origButtons = document.querySelector('form > .d-flex.justify-content-between');
  if (origButtons) origButtons.remove();
}

function goToStep(stepNumber) {
  // Скрываем все секции
  document.querySelectorAll('.section-card').forEach(section => {
    section.style.display = 'none';
  });

  // Показываем нужную секцию
  const targetSection = document.querySelector(`.section-card[data-step="${stepNumber}"]`);
  if (targetSection) targetSection.style.display = 'block';

  // Обновляем индикатор прогресса
  document.querySelectorAll('.progress-step').forEach(step => {
    const step_num = parseInt(step.dataset.step);
    step.classList.remove('active', 'completed');

    if (step_num < stepNumber) {
      step.classList.add('completed');
    } else if (step_num === stepNumber) {
      step.classList.add('active');
    }
  });

  // Прокручиваем страницу вверх
  window.scrollTo(0, 0);
}

function validateAndGoToStep(stepNumber) {
  // Валидация текущего шага перед переходом
  const currentStep = stepNumber - 1;
  const currentSection = document.querySelector(`.section-card[data-step="${currentStep}"]`);
  const inputs = currentSection.querySelectorAll('input[required], select[required], textarea[required]');

  let isValid = true;
  inputs.forEach(input => {
    if (!input.value.trim()) {
      input.classList.add('is-invalid');
      isValid = false;
    } else {
      input.classList.remove('is-invalid');
    }
  });

  if (isValid) {
    goToStep(stepNumber);
  } else {
    // Показать уведомление
    alert('Пожалуйста, заполните все обязательные поля');
  }
}