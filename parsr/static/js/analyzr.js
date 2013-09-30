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

        $("a[trigger=delete]").click(function() {
            var a = $(this);

            var result = confirm("Do you really want to delete the repo?");

            if(result) {
                $.ajax(a.attr("action"), {
                    type: "POST",
                    data: {
                        csrfmiddlewaretoken: $.cookie("csrftoken")
                    },
                    success: function() {
                        a.parents("tr").slideUp(function() {
                            $(this).remove();
                        });
                    }
                });
            }

            return false;
        });

        Punchcard.auto();
        FileStatistics.auto(".stats");
    });
}());
