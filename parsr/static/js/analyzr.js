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

        var targets = [];

        $(".nav li").each(function() {
            var li = $(this);

            li.find("a").each(function() {
                var a = $(this);

                var target = a.attr("data-target");

                if(!target) {
                    return;
                }

                targets.push(target);

                a.click(function() {
                    $.each(targets, function() {
                        $(this.toString()).hide();

                        $(".nav li").removeClass("active");
                    });

                    $(target).show();
                    a.parent("li").addClass("active");

                    return false;
                });

                $(target).hide();
            });

            if(li.hasClass("active")) {
                li.find("a").click();
            }
        });

        Punchcard.auto();
        FileStatistics.auto(".stats");
    });
}());
