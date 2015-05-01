define([
    "react",
    "jquery"
], function(
    React,
    $
) {

    return {

        getInitialState: function() {
            return {
                open: false
            };
        },

        componentDidMount: function() {
            $(document).on("click", this.handleDocumentClick);
        },

        componentWillUnmount: function() {
            $(document).off("click", this.handleDocumentClick);
        },

        getDropddown: function() {
            var node = $(React.findDOMNode(this));

            if(node.hasClass("dropdown")) {
                return node.get(0);
            }

            return node.find(".dropdown").get(0);
        },

        handleDocumentClick: function(event) {
            if(!this.state.open) {
                return;
            }

            if(event.target === React.findDOMNode(this)) {
                return;
            }

            var target = $(event.target);

            if(target.parents(".dropdown").get(0) === this.getDropddown()) {
                return;
            }

            this.close();
        },

        toggle: function(event) {
            this.setState({
                open: !this.state.open
            });
        },

        close: function() {
            this.setState({
                open: false
            });
        }
    };

});
