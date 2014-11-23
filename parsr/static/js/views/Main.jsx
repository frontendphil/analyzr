define([
    "react",

    "jsx!views/Header",
    "jsx!views/Footer"
], function(
    React,

    Header,
    Footer
) {
    return React.createClass({
        displayName: "Analyzr",

        render: function() {
            return (
                <div className="analyzr">
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
