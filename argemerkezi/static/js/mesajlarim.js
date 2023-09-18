$(document).ready(function () {
    // Mesaj gönderme formunu dinle
    $("#message-form").submit(function (e) {
        e.preventDefault();
        var form = $(this);

        $.ajax({
            url: form.attr("action"),
            method: form.attr("method"),
            data: form.serialize(),
            success: function (data) {
                // Mesaj gönderildiğinde burada işlem yapabilirsiniz
                // Örneğin, mesajları ekrana eklemek veya güncellemek için DOM manipülasyonu
            },
            error: function (xhr, errmsg, err) {
                // Hata durumunda burada işlem yapabilirsiniz
            }
        });
    });
});
