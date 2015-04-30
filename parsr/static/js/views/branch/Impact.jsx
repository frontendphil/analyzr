define([
    "react",

    "jsx!views/components/Hint"
], function(
    React,

    Hint
) {

    return React.createClass({

        displayName: "Impact",

        getInitialState: function() {
            return {
                loading: true
            };
        },

        render: function() {
            if(this.state.loading) {
                return (
                    <Hint loading={ true }>
                        Loading contributor impact...
                    </Hint>
                );
            }

            return (
                <div className="impact">
                </div>
            );
        }

    });

});
