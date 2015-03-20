define([
    "react",

    "jsx!views/components/QTip"
], function(
    React,

    QTip
) {

    return React.createClass({

        displayName: "PunchcardValue",

        getInitialState: function() {
            return {
                hover: false
            };
        },

        render: function() {
            var start = {
                h: 50,
                s: 45,
                l: 60
            };

            var end = 360;

            var value = this.props.value / this.props.max;

            var color = start.h + ((end-start.h) * value);

            return (
                <QTip value={ this.renderValue() }>
                    <div
                        className="circle"
                        onMouseEnter={ this.handleMouseEnter }
                        onMouseLeave={ this.handleMouseLeave }
                        style={ {
                            width: 20 * value,
                            height: 20 * value,
                            background: "hsl(" + color + "," + start.s + "%," + start.l + "%)",
                            borderColor: "hsl(" + color + "," + start.s + "%," + (start.l - 10) + "%)",
                            borderStyle: "solid",
                            borderWidth: this.state.hover ? 1 : 0
                        } }/>
                </QTip>
            );
        },

        renderValue: function() {
            return (
                <div className="value">
                    <b>{ this.props.value }</b> contributions
                </div>
            );
        },

        handleMouseEnter: function() {
            this.setState({
                hover: true
            });
        },

        handleMouseLeave: function() {
            this.setState({
                hover: false
            });
        }
    });

});
