$(document).ready(function () {
    function updateTotal() {
        let total = 0;
        $("tr").each(function () {
            const price = parseFloat($(this).find(".price").data("price"));
            const quantity = parseInt($(this).find("input[type='number']").val(), 10) || 0;
            total += price * quantity;
        });
        $("#total-sum").text(total);
    }

    $(".increment").on("click", function () {
        const input = $(this).siblings("input");
        const max = parseInt(input.attr("max"), 10);
        let value = parseInt(input.val(), 10);
        if (value < max) {
            input.val(value + 1);
            updateTotal();
        }
    });

    $(".decrement").on("click", function () {
        const input = $(this).siblings("input");
        const min = parseInt(input.attr("min"), 10);
        let value = parseInt(input.val(), 10);
        if (value > min) {
            input.val(value - 1);
            updateTotal();
        }
    });

    $("input[type='number']").on("input", function () {
        updateTotal();
    });

    function updateTotal() {
        let total = 0;
        $("tr").each(function () {
            const price = parseFloat($(this).find(".price").data("price"));
            const quantity = parseInt($(this).find("input[type='number']").val(), 10) || 0;
            
            // Проверяем, что цена и количество корректны
            if (!isNaN(price) && !isNaN(quantity)) {
                total += price * quantity;
            }
        });
        $("#total-sum").text(total.toFixed(2)); // Округляем до двух знаков после запятой
    }
});