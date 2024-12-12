$(document).ready(function() {
    let k = 0;
    $(".make_admin").click(function(event){
        console.log(k);
        if (k == 1) {
            k = 0;
        } else {
            alert("Вы уверены, что хотите сделать админом?\nКликните ещё раз, если да.");
        }
        k++;
        event.preventDefault();  // Отмена перехода по ссылке
    });
});
