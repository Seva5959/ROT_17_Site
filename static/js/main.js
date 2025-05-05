document.addEventListener('DOMContentLoaded', function() {
    // Обработка кнопок переключения
    document.body.addEventListener('click', function(e) {
        // Раскрытие/скрытие ответов
        if (e.target.classList.contains('toggle-btn')) {
            const answerBlock = e.target.nextElementSibling;
            const isHidden = answerBlock.style.maxHeight === '0px' || !answerBlock.style.maxHeight;

            answerBlock.style.maxHeight = isHidden ? answerBlock.scrollHeight + 'px' : '0';
            e.target.textContent = isHidden ? '▲ Скрыть' : '▼ Показать ответ';
        }

        // Копирование текста
        if (e.target.classList.contains('copy-btn')) {
            const input = e.target.previousElementSibling;
            input.select();
            document.execCommand('copy');

            const notification = document.createElement('div');
            notification.className = 'copy-notification';
            notification.textContent = 'Скопировано: ' + input.value;
            document.body.appendChild(notification);

            setTimeout(() => notification.remove(), 2000);
        }
    });

    // Автоматическое скрытие временных сообщений
    function setupFlashMessages() {
        // Обрабатываем и сообщения об ошибках, и сообщения об успехе
        const timedMessages = document.querySelectorAll('.alert-error_timed, .alert-success');

        timedMessages.forEach(msg => {
            // Устанавливаем начальную непрозрачность
            msg.style.opacity = '1';

            // Запускаем таймер
            setTimeout(() => {
                // Плавное исчезновение
                msg.style.opacity = '0';

                // Удаляем элемент после анимации
                setTimeout(() => {
                    if (msg.parentNode) {
                        msg.parentNode.removeChild(msg);
                    }
                }, 500);
            }, 3000);
        });
    }

    // Вызываем функцию при загрузке страницы
    setupFlashMessages();

    // Проверка на все решенные коды
    function checkAllSolved() {
        const cards = document.querySelectorAll('.card');
        const allSolved = Array.from(cards).every(card => card.classList.contains('solved'));
        return allSolved;
    }

    // Если все коды решены, показываем поздравление
    if (checkAllSolved()) {
        // Дополнительная проверка на наличие контейнера поздравления
        const congratsContainer = document.getElementById('congratsContainer');
        if (congratsContainer) {
            setTimeout(() => {
                toggleCongrats(true);
            }, 500);
        }
    }

    // Функция для управления окном поздравления
    window.toggleCongrats = function(show) {
        const container = document.getElementById('congratsContainer');
        if (container) {
            if (show) {
                container.style.display = 'flex';
                // Добавляем небольшую задержку для плавной анимации
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

    // Логирование кликов по навигации (для отладки)
    document.querySelectorAll('nav a').forEach(link => {
        link.addEventListener('click', (e) => {
            console.log('Навигация:', e.target.textContent, e.target.href);
        });
    });
});