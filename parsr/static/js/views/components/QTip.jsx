define([
    "react"
], function(
    React
) {

    return React.createClass({

        displayName: "QTip",

        getInitialState: function() {
            return {
                hover: false
            };
        },

        render: function() {
            return (
                <div
                    onMouseEnter={ this.handleMouseEnter }
                    onMouseLeave={ this.handleMouseLeave }
                    className="qtip">
                    { this.renderTip() }

                    { this.props.children }
                </div>
            );
        },

        renderTip: function() {
            if(!this.state.hover) {
                return;
            }

            return (
                <div className="tip">
                    { this.props.value }
                </div>
            );
        },

        handleMouseEnter: function() {
            this.setState({
                hover: true
            });
        },

        handleMouseLeave: function() {
            this.setState({
                hover: false
            });
        }

    });

});
