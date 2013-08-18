(function() {
    $(document).ready(function() {
        $(".analyze").click(function() {
            var rel = $(this).attr("rel");

            $.ajax(rel, {
                type: "POST",
                data: {
                    csrfmiddlewaretoken: $.cookie("csrftoken")
                }
            });

            // window.location.reload();

            return false;
        });
    });
}());
