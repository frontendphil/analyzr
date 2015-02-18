define([
    "react",

    "jsx!views/components/Hint"
], function(
    React,

    Hint
) {

    return React.createClass({

        displayName: "Contributors",

        getInitialState: function() {
            return {
                loading: true
            };
        },

        componentDidMount: function() {
            this.props.collection.once("sync", function() {
                this.setState({
                    loading: false
                });
            }, this);

            this.props.collection.fetch();
        },

        render: function() {
            if(this.state.loading) {
                return (
                    <Hint loading={ true }>
                        Loading contributors...
                    </Hint>
                );
            }

            return (
                <div className="contributors">
                </div>
            );
        }
    });

});
