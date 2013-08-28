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

        $(".punchard").each(function() {
            var punchard = $(this);

            var repo = punchard.attr("repo");
            var author = punchard.attr("author");

            var url = "/punchcard/repo/" + repo;

            if(author) {
                url = url + "/author/" + author;
            }

            $.ajax(url, {
                success: function(data) {
                    console.log(data);
                }
            })
        });
    });
}());
