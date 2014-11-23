define([
    "react"
], function(
    React
) {

    return React.createClass({

        displayName: "Footer",

        render: function() {
            return (
                <div className='footer hidden-print'>
                    <div className='container'>
                        <i className='icon-github'></i>
                        <a href='https://github.com/pxlplnt/analyzr'>analyzr</a>
                    </div>
                </div>
            );
        }
    })

});
