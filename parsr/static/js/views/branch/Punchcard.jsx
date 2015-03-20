define([
    "react",
    "underscore",

    "jsx!views/components/Hint",
    "jsx!views/branch/PunchcardValue"
], function(
    React,
    _,

    Hint,
    Value
) {

    return React.createClass({

        displayName: "Punch Card",

        getInitialState: function() {
            return {
                loading: true,
                printing: false
            };
        },

        componentDidMount: function() {
            this.props.model.once("sync", function() {
                this.setState({
                    loading: false
                });
            }, this);

            this.props.model.fetch();
        },

        render: function() {
            if(this.state.loading) {
                return (
                    <Hint loading={ true }>
                        Loading punchcard...
                    </Hint>
                );
            }

            return (
                <div className="punchcard">
                    <table className="table table-hover">
                        <thead>
                            { this.renderHeader() }
                        </thead>
                        <tbody>
                            { this.renderContent() }
                        </tbody>
                    </table>
                </div>
            );
        },

        renderHeader: function() {
            return (
                <tr>
                    <th>Day</th>

                    { _.map(_.range(25), function(hour) {
                        return (
                            <th>{ hour }</th>
                        );
                    }) }
                </tr>
            );
        },

        renderContent: function() {
            return _.map(this.props.model.weekdays(), function(day) {
                return (
                    <tr key={ day }>
                        <td className="day">{ day }</td>
                        { _.map(this.props.model.hours(), function(hour) {
                            return (
                                <td className="hour">
                                    { this.renderCircle(this.props.model.getValue(day, hour), this.props.model.getMax()) }
                                </td>
                            );
                        }, this) }
                    </tr>
                );
            }, this);
        },

        renderCircle: function(value, max) {
            if(!value) {
                return;
            }

            return <Value value={ value } max={ max } />;
        }

    });

});
