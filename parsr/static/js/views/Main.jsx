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
            var View = this.props.currentView;
            return (
                <div className="analyzr content">
                    <div className="content">
                        <Header />

                        <View { ...this.props } />
                    </div>
                    <Footer />
                </div>
            );
        }
    });
});
