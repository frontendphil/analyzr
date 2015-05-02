define([
    "react",
    "react-d3",

    "jsx!views/components/Hint"
], function(
    React,
    D3,

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

            this.props.collection.fetch({
                data: {
                    language: this.props.language
                }
            });
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

            if(!this.props.language) {
                return (
                    <Hint>
                        Please select a language to show the churn
                    </Hint>
                );
            }

            return (
                <div className="churn">
                    <D3.AreaChart data={ this.getData() } />
                </div>
            );
        },

        getData: function() {
            var additions = {
                label: "Additions",
                values: this.props.collection.getAdditions()
            };

            var deletions = {
                label: "Deletions",
                values: this.props.collection.getDeletions()
            };

            return [additions, deletions];
        }
    });

});
