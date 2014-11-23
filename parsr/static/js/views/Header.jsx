define([
    "react"
], function(
    React
) {

    return React.createClass({

        displayName: "Header",

        render: function() {
            return (
                <ul class='nav nav-pills'>
                    <li>
                        { this.renderBreadcrumb() }
                    </li>

                    { this.renderLogout() }
                    { this.renderBrachInfo() }
                </ul>
            );
        },

        renderBreadcrumb: function() {
            return (
                <ol class='breadcrumb'>
                    <li>
                        <a href='{% url "parsr.views.app.index" %}'>
                            <i class='icon-code'></i>
                            Analyzr
                        </a>
                    </li>
                </ol>
            );
        },

        renderLogout: function() {
            return (
                <li class='pull-right'>
                    <a href='/logout'>
                        <i class='icon icon-signout'></i>
                        Logout
                    </a>
                </li>
            );
        },

        renderBrachInfo: function() {
            return (
                <li class='pull-right branch-info'>

                </li>
            );
        }
    });

});
