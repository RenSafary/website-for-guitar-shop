$(document).ready(function () {
    let currentIndex = 0;
    const images = $('.slideshow-images img');
    const totalImages = images.length;

    function showNextImage() {
        images.removeClass('active'); // Убираем класс "active" у всех изображений
        currentIndex = (currentIndex + 1) % totalImages; // Считаем следующий индекс
        images.eq(currentIndex).addClass('active'); // Добавляем "active" только текущему изображению
    }

    setInterval(showNextImage, 5000); // Смена изображения каждые 5 секунд
});
