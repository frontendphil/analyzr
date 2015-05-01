define([
    "react"
], function(
    React
) {

    return React.createClass({

        displayName: "BranchItem",

        render: function() {
            return (
                <div className="branch-item" onClick={ this.props.onClick }>
                    <i className="icon icon-box" />

                    { this.props.model.get("name") }
                </div>
            );
        }
    });

});
