define([
    "react"
], function(
    React
) {

    return React.createClass({

        displayName: "Hint",

        render: function() {
            var cls = React.addons.classSet({
                "hint": true,
                "hint-loading": this.props.loading,
                "hint-view": this.props.view
            });

            return (
                <div className={ cls }>
                    { this.props.children }
                </div>
            );
        }
    });

});
