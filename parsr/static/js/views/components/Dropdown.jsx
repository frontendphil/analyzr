define([
    "react",
    "jquery",

    "jsx!views/components/Hint"
], function(
    React,
    $,

    Hint
) {

    return React.createClass({

        displayName: "Dropdown",

        render: function() {
            return (
                <div className={ "dropdown " + (this.props.open ? "open" : "") }>
                    { this.renderToggle() }
                    { this.renderOptions() }
                </div>
            );
        },

        renderToggle: function() {
            return (
                <div className="dropdown-toggle" onClick={ this.handleToggle }>
                    { this.props.toggle }
                </div>
            );
        },

        handleToggle: function(event) {
            event.preventDefault();
            event.stopPropagation();

            this.props.onToggle();
        },

        renderOptions: function() {
            return (
                <div className="dropdown-menu">
                    { this.props.children }
                </div>
            );
        }
    });

});
