(function() {

    $(document).ready(function() {
        $(".analyze").click(function() {
            var rel = $(this).attr("rel");

            $.ajax(rel, {
                type: "POST",
                beforeSend: function() {
                    window.setTimeout(function() {
                        window.location.reload();
                    }, 1000);
                },
                data: {
                    csrfmiddlewaretoken: $.cookie("csrftoken")
                }
            });

            return false;
        });

        Punchcard.auto();
        FileStatistics.auto(".stats");
    });
}());
