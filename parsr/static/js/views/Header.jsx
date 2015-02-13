define([
    "react"
], function(
    React
) {

    return React.createClass({

        displayName: "Header",

        render: function() {
            return (
                <ul className='nav nav-pills'>
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
                <ol className='breadcrumb'>
                    <li>
                        <a href='/'>
                            <i className='fa fa-code'></i>
                            Analyzr
                        </a>
                    </li>
                </ol>
            );
        },

        renderLogout: function() {
            return (
                <li className='pull-right'>
                    <a href='/logout'>
                        <i className='fa fa-power-off'></i>
                        Logout
                    </a>
                </li>
            );
        },

        renderBrachInfo: function() {
            return (
                <li className='pull-right branch-info'>

                </li>
            );
        }
    });

});
