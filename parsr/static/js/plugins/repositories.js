ns("plugins");

(function() {

    var REFRESH_INTERVAL = 30 * 1000;

    analyzr.plugins.Repositories = analyzr.core.Observable.extend({

        init: function(target) {
            this._super();

            this.dom = $(target);
        },

        prepareTable: function() {
            return $(
                "<table class='table table-hover'>" +
                    "<thead>" +
                        "<tr>" +
                            "<th class='status'>" +
                                "<abbr title='At least one branch analyzed'>A</abbr>" +
                            "</th>" +
                            "<th class='status'>" +
                                "<abbr title='At least one branch measured'>M</abbr>" +
                            "</th>" +
                            "<th class='status'>" +
                                "<abbr title='Anonymous repo access'>S</abbr>" +
                            "</th>" +
                            "<th>Type</th>" +
                            "<th>Location</th>" +
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
            cls = cls || "icon-code icon-blank";

            return $("<i class='icon-li " + cls + "'></i>");
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
            if(repo.rep.busy || !repo.rep.analyzed) {
                return this.wrap(repo.rep.name);
            }

            return this.wrap($(
                "<a href='" + repo.view + "'>" + repo.rep.name + "</a>"
            ));
        },

        getRepoStatus: function(repo) {
            if(repo.anonymous) {
                return this.icon("icon-unlock-alt");
            }

            return this.icon("icon-lock");
        },

        createDropdown: function(name, repo, clb) {
            var container = $(
                "<div class='btn-group'>" +
                    "<button type='button' class='btn btn-default btn-sm dropdown-toggle' data-toggle='dropdown'>" +
                        name + " <span class='caret'></span>" +
                    "</button>" +
                    "<ul class='dropdown-menu icons-ul' role='menu'>" +
                        "<li class='loading'>" +
                            "<i class='icon-li icon-spinner icon-spin'></i>Loading..." +
                        "</li>" +
                    "</ul>" +
                "</div>"
            );

            var dropdown = container.find("ul");

            container.one("click", function() {
                $.ajax(repo.href + "/branches", {
                    success: function(branches) {
                        container.find(".loading").remove();

                        $.each(branches, function() {
                            var item = $("<li />");
                            var content = clb(this);

                            if(!content) {
                                return;
                            }

                            item.append(content);
                            dropdown.append(item);
                        });
                    }
                });
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

        reload: function() {
            window.setTimeout(function() {
                window.location.reload();
            }, 100);
        },

        showResumeDialog: function(link, error) {
            var that = this;

            var text = "This action has been interrupted before. " +
                    "Would you like to resume where you left off, or start over?";

            if(error) {
                text += error;
            }

            var dialog = new analyzr.plugins.Dialog({
                width: 500,
                text: text,
                actions: [
                    {
                        text: "Cancel",
                        handler: function(dialog) {
                            dialog.remove();
                        }
                    },
                    {
                        text: "Restart",
                        handler: function() {
                            that.request(link.data("rel"));
                            that.reload();
                        }
                    },
                    {
                        text: "Resume",
                        cls: "btn-primary",
                        handler: function() {
                            that.request(link.data("rel") + "/resume");
                            that.reload();
                        }
                    }
                ]
            });

            dialog.show();
        },

        createLink: function(branch, action, clb) {
            var that = this;

            var link = $(
                "<a href='#' data-rel='" + branch.href + "/" + action + "'>" +
                    branch.rep.name +
                "</a>"
            );

            link.click(function() {
                var url = $(this).data("rel");

                var performAction = function() {
                    if(clb && !clb(link, branch)) {
                        return false;
                    }

                    that.request(url);
                    that.reload();
                };

                if(branch.rep[action].finished) {
                    analyzr.plugins.Dialog.confirm("This action has already finished on the selected branch. Do you want to restart it?", performAction);
                } else {
                    performAction();
                }

                return false;
            });

            return link;
        },

        createAction: function(title, action, repo, filter) {
            var that = this;

            filter = filter || function() { return true; };

            return this.createDropdown(title, repo, function(branch) {
                if(!filter(branch)) {
                    return false;
                }

                var link = that.createLink(branch, action, function(link, branch) {
                    if(!branch.rep[action].interrupted && !branch.rep[action].lastError) {
                        return true;
                    }

                    that.showResumeDialog(link, branch.rep[action].lastError);

                    return false;
                });

                if(branch.rep[action].finished) {
                    link.prepend(that.icon("icon-ok"));
                }

                if(branch.rep[action].interrupted || branch.rep[action].lastError) {
                    link.prepend(that.icon("icon-warning-sign"));
                }

                if(link.find(".icon-li").length === 0) {
                    link.prepend(that.icon());
                }

                return link;
            });
        },

        createActions: function(repo) {
            var rep = repo.rep;

            if(rep.busy) {
                var status = rep.status;

                if(status.action === "analyzing") {
                    return this.wrap("Analyzing branch " + status.rep.rep.name + "...");
                }

                return this.wrap("Measuring branch " + status.rep.rep.name + "...");
            }

            var wrap = this.wrap(this.createAction("Analyze", "analyze", repo));

            if(!rep.measurable) {
                return wrap;
            }

            wrap.append(this.createAction("Measure", "measure", repo, function(branch) {
                return branch.rep.analyze.finished;
            }));

            return wrap;
        },

        createRepo: function(info) {
            var that = this;
            var repo = $("<tr data-href='" + info.href + "' />");

            var rep = info.rep;

            repo.append(this.getAnalyzingState(rep));
            repo.append(this.getMeasuringState(rep));
            repo.append(this.wrap(this.getRepoStatus(rep), {
                "class": "status"
            }));
            repo.append(this.wrap(rep.kind));
            repo.append(this.getRepoLink(info));

            repo.append(this.createActions(info));

            var edit = "", remove = "", purge = "";

            if(!rep.busy) {
                edit = $("<a href='" + info.href + "/edit' class='btn btn-default' />");
                edit.append(this.icon("icon-edit"));

                remove = $("<a href='#' title='Remove this repository' data-action='" + info.href + "/remove' class='btn btn-danger'/>");
                remove.append(this.icon("icon-remove"));

                remove.click(function() {
                    analyzr.plugins.Dialog.confirm("Do you really want to delete the repo?", function() {
                        that.request(remove.data("action"), function() {
                            $("tr[data-href='" + info.href + "']").fadeOut(function() {
                                $(this).remove();
                            });
                        });
                    });

                    return false;
                });

                purge = $("<a href='#' title='Clear data of this repository' data-action='" + info.href + "/purge' class='btn btn-warning' />");
                purge.append(this.icon("icon-folder-close-alt"));

                if(!rep.checkedOut) {
                    purge.prop("readonly", true);
                    purge.addClass("disabled");
                }

                purge.click(function() {
                    analyzr.plugins.Dialog.confirm("Do you really want to delete all files belonging to this repository?", function() {
                        var mask = new analyzr.core.Mask(that.dom, "Removing files...");
                        mask.show();

                        that.request(purge.data("action"), function() {
                            mask.remove();
                        });
                    });

                    return false;
                });
            }

            repo.append(this.wrap([edit, purge, remove], { "class": "actions" }));

            return repo;
        },

        createStatusIndicator: function(repo, branch, action) {
            if(branch.rep.activity.action !== action) {
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
                $.ajax(branch.href, {
                    success: function(branch) {
                        if(typeof branch.rep.activity.progress === "undefined") {
                            container.fadeOut(function() {
                                that.load();
                            });

                            return;
                        }

                        var progress = (100 *  branch.rep.activity.progress / branch.rep.activity.count);

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

            var mask = new analyzr.core.Mask(this.dom, "Loading repositories...");
            mask.show();

            var table = this.prepareTable();

            this.dom.append(table);

            var body = table.find("tbody");

            $.ajax("/repositories", {
                success: function(repositories) {
                    $.each(repositories, function() {
                        var repo = that.createRepo(this);
                        body.append(repo);

                        if(this.rep.status.action !== "ready") {
                            var progess = that.createStatusIndicator(repo, this.rep.status.rep, this.rep.status.action);
                            body.append(progess);
                        }
                    });

                    mask.remove();
                }
            });
        }

    });

}());
