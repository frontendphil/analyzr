define([
    "react",

    "views/mixins/BackboneMixin"
], function(
    React,

    BackboneMixin
) {

    return React.createClass({
        displayName: "Repository",

        render: function() {
            return (
                <tr>
                    { this.renderState() }
                </tr>
            );
        },

        renderState: function() {
            return (
                <td className="status">
                    { this.getStatusIcon({
                        running: this.props.model.get("analyzing"),
                        finished: this.props.model.get("analyzed")
                    })}
                </td>
            );
        },

        getStatusIcon: function(status) {
            if(status.running) {
                return this.icon("fa-refresh fa-spin");
            }

            if(status.finished) {
                return this.icon("fa-check");
            }

            return this.icon("fa-question");
        },

        icon: function(cls) {
            cls = cls || "fa-code fa-blank";

            return <i className={"fa fa-li " + cls }></i>;
        },
    });

});
