define([
    "react",
    "jquery",

    "singleton/Router",

    "jsx!views/Header",
    "jsx!views/Footer"
], function(
    React,
    $,

    Router,

    Header,
    Footer
) {
    return React.createClass({

        displayName: "Analyzr",

        componentDidMount: function() {
            $(document).on("click", "a", function(event) {
                var href = $(this).attr("href");

                if(!href || href === "#") {
                    return;
                }

                event.preventDefault();

                Router.navigate(href, {
                    trigger: true
                });
            });
        },

        render: function() {
            return (
                <div className="analyzr content">
                    <div className="content">
                        <Header />

                        { this.props.currentView(this.props) }
                    </div>
                    <Footer />
                </div>
            );
        }
    });
});
