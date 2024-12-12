$(document).ready(function() {
    $('#login-form').on('submit', function(event) {
        event.preventDefault(); // Предотвращаем стандартное поведение отправки формы

        var formData = $(this).serialize(); // Сериализуем данные формы

        $.ajax({
            type: 'POST',
            url: '/sign-in',
            data: formData,
            success: function(response) {
                // Если сервер возвращает успешный ответ, перенаправляем пользователя на главную страницу
                window.location.href = '/';
            },
            error: function(xhr, status, error) {
                // Если сервер возвращает ошибку, выводим алерт
                if (xhr.status === 401) {
                    alert('Логин или пароль введены неверно. Пожалуйста, попробуйте снова.');
                } else {
                    alert('Произошла ошибка. Пожалуйста, попробуйте позже.');
                }
            }
        });
    });
});