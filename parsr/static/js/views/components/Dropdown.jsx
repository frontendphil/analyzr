define([
    "react",
    "jquery",

    "jsx!views/components/Hint"
], function(
    React,
    $,

    Hint
) {

    return React.createClass({

        displayName: "Dropdown",

        getInitialState: function() {
            return {
                loading: false,
                open: false
            };
        },

        componentDidMount: function() {
            $(document).on("click", this.handleDocumentClick);
        },

        componentWillUnmount: function() {
            $(document).off("click", this.handleDocumentClick);
        },

        componentDidUpdate: function(prevProps, prevState) {
            if(!this.props.collection) {
                return;
            }

            if(!this.state.open || prevState.open === this.state.open) {
                return;
            }

            this.setState({
                loading: true
            });

            this.props.collection.once("sync", function() {
                this.setState({
                    loading: false
                });
            }, this);

            this.props.collection.fetch();
        },

        handleDocumentClick: function(event) {
            if(!this.state.open) {
                return;
            }

            if(event.target === this.getDOMNode()) {
                return;
            }

            var target = $(event.target);

            if(target.parents(".dropdown").get(0) === this.getDOMNode()) {
                return;
            }

            this.close();
        },

        render: function() {
            return (
                <div className={ "dropdown " + (this.state.open ? "open" : "") }>
                    <button className="btn btn-default btn-sm dropdown-toggle" onClick={ this.toggle }>
                        { this.props.title }

                        { this.renderIcon() }
                    </button>

                    { this.renderOptions() }
                </div>
            );
        },

        toggle: function(event) {
            event.preventDefault();
            event.stopPropagation();

            this.setState({
                open: !this.state.open
            });
        },

        close: function() {
            this.setState({
                open: false
            });
        },

        renderOptions: function() {
            if(!this.state.open) {
                return;
            }

            return (
                <ul className="dropdown-menu fa-ul">
                    { this.renderContents() }
                </ul>
            );
        },

        renderContents: function() {
            if(this.props.collection) {
                return this.renderCollection();
            }

            return this.renderItems();
        },

        renderIcon: function() {
            if(this.state.open) {
                return <i className="fa fa-angle-up"></i>;
            }

            return <i className="fa fa-angle-down"></i>;
        },

        renderCollection: function() {
            if(this.state.loading) {
                return (
                    <li className="loading disabled fa-li">
                        <Hint loading={ true }>
                            Loading...
                        </Hint>
                    </li>
                );
            }

            return this.props.collection.map(function(item) {
                return (
                    <li className="fa-li">
                        <a href="#" onClick={ this.handleSelect.bind(null, item) }>
                            { this.props.renderItem(item) }
                        </a>
                    </li>
                );
            }, this);
        },

        handleSelect: function(item, event) {
            event.preventDefault();

            this.props.onSelect(item);
        }
    });

});
