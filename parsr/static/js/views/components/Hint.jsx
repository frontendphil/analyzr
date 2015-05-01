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
                "hint-inline": this.props.inline,
                "hint-loading": this.props.loading,
                "hint-view": this.props.view
            });

            return (
                <div className={ cls }>
                    <span className="message">
                        { this.props.children }
                    </span>
                </div>
            );
        }
    });

});
