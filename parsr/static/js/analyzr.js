(function() {

    $(document).ready(function() {
        var asyncAction = function() {
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
        };

        $(".analyze").click(asyncAction);
        $(".measure").click(asyncAction);

        $("select.branch").change(function() {
            var branch = $(this).find("option:selected").attr("value");
            var repo = $(this).data("repo");

            window.location.href = "/repo/" + repo + "/branch/" + branch;
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

            var changeContent = function(target, targets) {
                $.each(targets, function() {
                    $(this.toString()).hide();

                    $(".nav li").removeClass("active");
                });

                $("." + target)
                    .show();

                $("*[data-target=" + target + "]").parent("li").addClass("active");
            };

            li.find("a").each(function() {
                var a = $(this);

                var target = a.attr("data-target");

                if(!target) {
                    return;
                }

                targets.push("." + target);

                a.click(function() {
                    changeContent(target, targets);
                    window.location.hash = target;

                    return false;
                });

                $("." + target).hide();
            });

            if(window.location.hash) {
                var target = window.location.hash.replace("#", "");

                changeContent(target, targets);
            }

            if(li.hasClass("active")) {
                li.find("a").click();
            }
        });

        Punchcard.auto();
        FileStatistics.auto(".stats");
    });
}());
