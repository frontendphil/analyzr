define([
    "react",

    "react-bootstrap/Modal"
], function(
    React,

    Modal
) {

    return React.createClass({

        displayName: "Dialog",

        render: function() {
            return (
                <Modal title={ this.props.title } onRequestHide={ this.props.onRequestHide }>
                    <div className="modal-body">
                        { this.props.children }
                    </div>

                    { this.renderActions() }
                </Modal>
            );
        },

        renderActions: function() {
            if(!this.props.actions) {
                return (
                    <div className="modal-footer">
                        <button className="btn btn-default" onClick={ this.props.onRequestHide }>
                            Dismiss
                        </button>
                    </div>
                );
            }

            return (
                <div className="modal-footer">
                    { this.props.actions }
                </div>
            );
        }
    });

});
