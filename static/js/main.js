document.addEventListener('DOMContentLoaded', function() {
    // Инициализация всех функций
    initApp();
    // Скрываем все ответы при загрузке
    hideAllAnswers();
});

// Новая функция для скрытия всех ответов
function hideAllAnswers() {
    document.querySelectorAll('.answer-block').forEach(block => {
        // Проверяем, не скрыт ли уже блок (чтобы не сбрасывать анимацию)
        if (block.style.maxHeight !== '0px') {
            block.style.maxHeight = '0px';
            // Устанавливаем transition только если ещё не задан
            if (!block.style.transition) {
                block.style.transition = 'max-height 0.3s ease';
            }
        }
    });
}

// Функция инициализации приложения
function initApp() {
    setupEventDelegation();
    setupFlashMessages();
    checkAllSolved();

    // Инициализация счетчика сообщений для админа
    if (document.getElementById('messageCount')) {
        updateMessageCount();
        setInterval(updateMessageCount, 30000);
    }
}

// Настройка делегирования событий
function setupEventDelegation() {
    document.body.addEventListener('click', function(e) {
        // Обработка кнопок переключения (показать/скрыть ответ)
        if (e.target.classList.contains('toggle-btn')) {
            handleToggleButton(e.target);
        }

        // Обработка кнопок копирования
        if (e.target.classList.contains('copy-btn')) {
            handleCopyButton(e.target);
        }
    });
}

// Обработка кнопок переключения
function handleToggleButton(button) {
    const answerBlock = button.nextElementSibling;

    // 1. Проверка блока
    if (!answerBlock) {
        showDebugMessage('Блок ответа не найден!', true);
        return;
    }

    // 2. Определение состояния на основе computed style
    const computedStyle = window.getComputedStyle(answerBlock);
    const isHidden = computedStyle.maxHeight === '0px' ||
                     parseInt(computedStyle.maxHeight) === 0;

    // 3. Переключение
    if (isHidden) {
        // Показываем ответ
        answerBlock.style.transition = 'max-height 0.3s ease';
        answerBlock.style.maxHeight = `${answerBlock.scrollHeight}px`;
        button.textContent = '▲ Скрыть';
    } else {
        // Скрываем ответ
        answerBlock.style.transition = 'max-height 0.3s ease';
        answerBlock.style.maxHeight = '0px';
        button.textContent = '▼ Показать ответ';
    }

    // 4. Отладочное сообщение
    showDebugMessage(`Состояние: ${isHidden ? 'показано' : 'скрыто'} (${computedStyle.maxHeight})`);
}

// Улучшенный вывод сообщений
function showDebugMessage(msg, isError = false) {
    const debugDiv = document.getElementById('debug-messages') || createDebugDiv();
    debugDiv.innerHTML = `<p style="color: ${isError ? 'red' : 'black'}">${msg}</p>`;

    // Автоочистка через 3 секунды
    setTimeout(() => debugDiv.innerHTML = '', 3000);
}
// Обработка кнопок копирования
function handleCopyButton(btn) {
    const input = btn.previousElementSibling;
    copyToClipboardElement(input);

    // Создаем всплывающее уведомление
    const notification = document.createElement('div');
    notification.className = 'copy-notification';
    notification.textContent = 'Скопировано: ' + input.value;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 500);
    }, 1500);
}

// Копирование в буфер обмена (универсальная функция)
window.copyToClipboard = function(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        copyToClipboardElement(element);
    }
};

// Копирование элемента в буфер обмена
function copyToClipboardElement(element) {
    element.select();
    document.execCommand('copy');

    // Показываем уведомление о копировании
    const successMessage = document.querySelector('.copy-success-message');
    if (successMessage) {
        successMessage.style.display = 'block';
        setTimeout(() => {
            successMessage.style.display = 'none';
        }, 2000);
    }

    // Для постоянной ссылки внизу страницы
    const permanentSuccess = document.getElementById('permanentLinkSuccess');
    if (permanentSuccess) {
        permanentSuccess.style.display = 'block';
        setTimeout(() => {
            permanentSuccess.style.display = 'none';
        }, 2000);
    }
}

// Автоматическое скрытие временных сообщений
function setupFlashMessages() {
    const timedMessages = document.querySelectorAll('.alert-error_timed, .alert-success');

    timedMessages.forEach(msg => {
        msg.style.opacity = '1';

        setTimeout(() => {
            msg.style.opacity = '0';
            setTimeout(() => {
                if (msg.parentNode) {
                    msg.parentNode.removeChild(msg);
                }
            }, 500);
        }, 3000);
    });
}

// Проверка на все решенные коды
function checkAllSolved() {
    const cards = document.querySelectorAll('.card');
    if (cards.length === 0) return false;

    const allSolved = Array.from(cards).every(card => card.classList.contains('solved'));

    if (allSolved) {
        const congratsContainer = document.getElementById('congratsContainer');
        if (congratsContainer) {
            setTimeout(() => {
                toggleCongrats(true);
            }, 500);
        }
    }

    return allSolved;
}

// Управление окном поздравления
window.toggleCongrats = function(show) {
    const container = document.getElementById('congratsContainer');
    if (container) {
        if (show) {
            container.style.display = 'flex';
            setTimeout(() => {
                container.style.opacity = '1';
            }, 10);
        } else {
            container.style.opacity = '0';
            setTimeout(() => {
                container.style.display = 'none';
            }, 500);
        }
    }
};

// Обработка подсказок для пользователя
window.showHint = function(step, codeId) {
    const modal = document.getElementById('hintModal');
    const image = document.getElementById('hintImage');
    const text = document.getElementById('hintText');
    const nextBtn = document.getElementById('hintNext');
    const backBtn = document.getElementById('hintBack');
    const adminForm = document.getElementById('adminMessageForm');
    const currentCodeId = codeId;

    adminForm.style.display = 'none';

    switch(step) {
        case 1:
            image.src = "/static/image/cat_1.png";
            text.textContent = "Не получается разгадать шифр?";
            nextBtn.textContent = "Да";
            break;
        case 2:
            image.src = "/static/image/cat_2.png";
            text.textContent = "Вы уверены, что не допустили ошибки?";
            nextBtn.textContent = "Да";
            break;
        case 3:
            image.src = "/static/image/cat_3.png";
            text.textContent = "Вы не забыли, что шифр включает верхний регистр?";
            nextBtn.textContent = "Не забыла";
            break;
        case 4:
            image.src = "/static/image/cat_4.png";
            text.textContent = "Написать Админу?";
            nextBtn.style.display = 'none';
            adminForm.style.display = 'block';
            break;
    }

    modal.style.display = 'flex';

    backBtn.onclick = function() {
        modal.style.display = 'none';
    };

    nextBtn.onclick = function() {
        if (step < 4) {
            showHint(step + 1, currentCodeId);
        }
    };

    document.getElementById('sendAdminMessage').onclick = function() {
        const messageText = document.getElementById('adminMessageText').value;
        if (messageText.trim() === '') {
            alert('Пожалуйста, введите сообщение');
            return;
        }

        fetch('/send_message_to_admin', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `code_id=${currentCodeId}&message=${encodeURIComponent(messageText)}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Сообщение отправлено администратору');
                modal.style.display = 'none';
            } else {
                alert('Ошибка при отправке сообщения: ' + data.error);
            }
        })
        .catch(error => {
            alert('Произошла ошибка: ' + error);
        });
    };
};

// Обновление счетчика непрочитанных сообщений
function updateMessageCount() {
    fetch('/admin/unread_messages_count')
        .then(response => response.json())
        .then(data => {
            const messageCount = document.getElementById('messageCount');
            if (messageCount) {
                if (data.count > 0) {
                    messageCount.textContent = data.count;
                    messageCount.style.display = 'inline-block';
                } else {
                    messageCount.style.display = 'none';
                }
            }
        })
        .catch(error => console.error('Ошибка при получении счетчика сообщений:', error));
}