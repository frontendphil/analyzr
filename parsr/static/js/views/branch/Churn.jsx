define([
    "react",

    "jsx!views/components/Hint"
], function(
    React,

    Hint
) {

    return React.createClass({

        displayName: "Churn",

        getInitialState: function() {
            return {
                loading: true
            };
        },

        componentWillMount: function() {
            this.props.collection.once("sync", function() {
                this.setState({
                    loading: false
                });
            }, this);

            this.props.collection.fetch();
        },

        componentWillUnmount: function() {
            this.props.collection.off(null, null, this);
        },

        render: function() {
            if(this.state.loading) {
                return (
                    <Hint loading={ true }>
                        Loading churn...
                    </Hint>
                );
            }

            return (
                <div className="churn">
                </div>
            );
        }
    });

});
