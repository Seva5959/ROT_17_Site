document.addEventListener('DOMContentLoaded', function() {
    // Находим все кнопки переключения
    const toggleButtons = document.querySelectorAll('.toggle-btn');

    // Добавляем обработчик для каждой кнопки
    toggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const answerBlock = this.nextElementSibling;
            const isHidden = answerBlock.style.maxHeight === '0px' ||
                           !answerBlock.style.maxHeight;

            // Плавное раскрытие/скрытие
            if (isHidden) {
                answerBlock.style.maxHeight = answerBlock.scrollHeight + 'px';
                this.textContent = '▲ Скрыть';
            } else {
                answerBlock.style.maxHeight = '0';
                this.textContent = '▼ Показать ответ';
            }
        });
    });

    // Обработчики для кнопок копирования
    document.querySelectorAll('.copy-btn').forEach(button => {
        button.addEventListener('click', function() {
            const input = this.previousElementSibling;
            input.select();
            document.execCommand('copy');

            // Создаем уведомление
            const notification = document.createElement('div');
            notification.className = 'copy-notification';
            notification.textContent = 'Скопировано!';
            document.body.appendChild(notification);

            setTimeout(() => {
                notification.remove();
            }, 2000);
        });
    });
});

// Обработчики для раскрытия блоков
document.addEventListener('DOMContentLoaded', function() {
    // Делегирование событий для динамически созданных элементов
    document.body.addEventListener('click', function(e) {
        if (e.target.classList.contains('toggle-btn')) {
            const answerBlock = e.target.nextElementSibling;
            answerBlock.style.display =
                answerBlock.style.display === 'block' ? 'none' : 'block';
            e.target.textContent =
                answerBlock.style.display === 'block' ? '▲ Скрыть' : '▼ Показать ответ';
        }

        if (e.target.classList.contains('copy-btn')) {
            const input = e.target.previousElementSibling;
            input.select();
            document.execCommand('copy');
            alert('Скопировано: ' + input.value);
        }
    });
});

document.querySelectorAll('nav a').forEach(link => {
    link.addEventListener('click', (e) => {
        console.log('Нажата ссылка:', e.target.href);
    });
});