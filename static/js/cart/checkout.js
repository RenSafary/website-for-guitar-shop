$(document).ready(function () {
    let seconds = 5; // Время до перенаправления
    const interval = setInterval(function () {
        $("#redirect-timer").text(seconds); // Обновление таймера
        seconds--;
        if (seconds < 0) {
            clearInterval(interval); // Остановка таймера
            window.location.href = "/"; // Перенаправление на главную
        }
    }, 1000); // Интервал обновления (1 секунда)
});