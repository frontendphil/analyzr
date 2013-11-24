var Repositories;

(function() {

    var REFRESH_INTERVAL = 30 * 1000;

    Repositories = Observeable.extend({

        init: function(target) {
            this._super();

            this.dom = $(target);
        },

        prepareTable: function() {
            return $(
                "<table class='table'>" +
                    "<thead>" +
                        "<tr>" +
                            "<th class='status'>" +
                                "<abbr title='At least one branch analyzed'>A</abbr>" +
                            "</th>" +
                            "<th class='status'>" +
                                "<abbr title='At least one branch measured'>M</abbr>" +
                            "</th>" +
                            "<th>Location</th>" +
                            "<th class='status'>" +
                                "<abbr title='Anonymous repo access'>S</abbr>" +
                            "</th>" +
                            "<th>Type</th>" +
                            "<th># Branches</th>" +
                            "<th># Authors</th>" +
                            "<th></th>" +
                            "<th></th>" +
                            "<th></th>" +
                        "</tr>" +
                    "</thead>" +
                    "<tbody>" +
                    "</tbody>" +
                "</table>"
            );
        },

        wrap: function(child, attrs) {
            var td = $("<td />");

            if(attrs) {
                $.each(attrs, function(key, value) {
                    td.attr(key, value);
                });
            }

            td.append(child);

            return td;
        },

        icon: function(cls) {
            return $("<i class='" + cls + "'></i>");
        },

        getAnalyzingState: function(repo) {
            var icon = this.getStatusIcon({
                running: repo.analyzing,
                finished: repo.analyzed
            });

            return this.wrap(icon, {
                "class": "status"
            });
        },

        getMeasuringState: function(repo) {
            var icon = this.getStatusIcon({
                running: repo.measuring,
                finished: repo.measured
            });

            return this.wrap(icon, {
                "class": "status"
            });
        },

        getStatusIcon: function(status) {
            if(status.running) {
                return this.icon("icon-refresh icon-spin");
            }

            if(status.finished) {
                return this.icon("icon-ok");
            }

            return this.icon("icon-question");
        },

        getRepoLink: function(repo) {
            if(repo.busy || !repo.analyzed) {
                return this.wrap(repo.name);
            }

            return this.wrap($(
                "<a href='" + repo.href + "'>" + repo.name + "</a>"
            ));
        },

        getRepoStatus: function(repo) {
            if(repo.anonymous) {
                return this.icon("icon-unlock-alt");
            }

            return this.icon("icon-lock");
        },

        createDropdown: function(name, items, clb) {
            var container = $(
                "<div class='btn-group'>" +
                    "<button type='button' class='btn btn-default btn-sm dropdown-toggle' data-toggle='dropdown'>" +
                        name + " <span class='caret'></span>" +
                    "</button>" +
                    "<ul class='dropdown-menu' role='menu'>" +
                    "</ul>" +
                "</div>"
            );

            var dropdown = container.find("ul");

            $.each(items, function() {
                var item = $("<li />");
                var content = clb(this);

                if(!content) {
                    return;
                }

                item.append(content);
                dropdown.append(item);
            });

            return container;
        },

        request: function(url, clb) {
            if(!url) {
                return;
            }

            $.ajax(url, {
                type: "POST",
                data: {
                    csrfmiddlewaretoken: $.cookie("csrftoken")
                },
                success: clb
            });
        },

        createActions: function(repo) {
            if(repo.busy) {
                var status = repo.status;

                if(status.action === "analyzing") {
                    return this.wrap("Analyzing branch " + status.rep.name + "...");
                }

                return this.wrap("Measuring branch " + status.rep.name + "...");
            }

            var that = this;

            var createLink = function(branch, action) {
                var link = $(
                    "<a href='#' data-rel='" + branch.href + "/" + action + "'>" +
                        branch.name +
                    "</a>"
                );

                link.click(function() {
                    that.request($(this).data("rel"));

                    window.setTimeout(function() {
                        window.location.href = window.location.href;
                    }, 100);

                    return false;
                });

                return link;
            };

            var wrap = this.wrap(this.createDropdown("Analyze", repo.branches, function(branch) {
                var link = createLink(branch, "analyze");

                if(branch.analyzed) {
                    link.append(that.icon("icon-ok"));
                }

                return link;
            }));

            if(!repo.measurable) {
                return wrap;
            }

            wrap.append(this.createDropdown("Measure", repo.branches, function(branch) {
                if(!branch.analyzed) {
                    return;
                }

                var link = createLink(branch, "measure");

                if(branch.measured) {
                    link.append(that.icon("icon-ok"));
                }

                return link;
            }));

            return wrap;
        },

        createRepo: function(info) {
            var that = this;
            var repo = $("<tr data-href='" + info.href + "' />");

            repo.append(this.getAnalyzingState(info));
            repo.append(this.getMeasuringState(info));
            repo.append(this.getRepoLink(info));
            repo.append(this.wrap(this.getRepoStatus(info), {
                "class": "status"
            }));

            repo.append(this.wrap(info.kind));
            repo.append(this.wrap(info.branchCount));
            repo.append(this.wrap(info.authorCount));

            repo.append(this.createActions(info));

            var edit = "", remove = "";

            if(!info.busy) {
                edit = $("<a href='" + info.href + "/edit' />");
                edit.append(this.icon("icon-edit"));

                remove = $("<a href='#' data-action='" + info.href + "/remove' />");
                remove.append(this.icon("icon-remove"));

                remove.click(function() {
                    var result = confirm("Do you really want to delete the repo?");

                    if(!result) {
                        return false;
                    }

                    that.request($(this).data("action"), function() {
                        $("tr[data-href='" + info.href + "']").fadeOut(function() {
                            $(this).remove();
                        });
                    });

                    return false;
                });
            }

            repo.append(this.wrap(edit), this.wrap(remove));

            return repo;
        },

        createStatusIndicator: function(repo, branch, action) {
            if(branch.activity.action !== action) {
                return;
            }

            var container = $(
                "<tr class='progress progress-striped active'>" +
                    "<td colspan='" + repo.children().length + "'>" +
                        "<div class='progress-bar' role='progressbar'></div>" +
                    "</td>" +
                "</tr>"
            );

            var that = this;

            var updateProgress = function() {
                $.ajax(branch.href + "/info", {
                    success: function(data) {
                        if(!data.activity) {
                            container.fadeOut(function() {
                                that.load();
                            });

                            return;
                        }

                        var progress = (100 *  data.activity.progress / data.activity.count);

                        container.find(".progress-bar").css({
                            width: progress + "%"
                        });

                        if(progress !== 0 && !progress) {
                            window.setTimeout(updateProgress, REFRESH_INTERVAL);

                            return;
                        }

                        if(progress < 100) {
                            container.find(".progress-bar").html(Math.round(progress) + "%");

                            window.setTimeout(updateProgress, REFRESH_INTERVAL);
                        } else {
                            container.fadeOut(function() {
                                that.load();
                            });
                        }
                    }
                });
            };

            updateProgress();

            return container;
        },

        load: function() {
            var that = this;

            this.dom.html("");

            var table = this.prepareTable();

            this.dom.append(table);

            var body = table.find("tbody");

            $.ajax("/repositories", {
                success: function(repositories) {
                    $.each(repositories, function() {
                        var repo = that.createRepo(this);
                        body.append(repo);

                        if(this.status.action !== "ready") {
                            var progess = that.createStatusIndicator(repo, this.status.rep, this.status.action);
                            body.append(progess);
                        }
                    });
                }
            });
        }

    });

}());
