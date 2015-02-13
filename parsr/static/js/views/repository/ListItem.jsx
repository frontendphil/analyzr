define([
    "react",

    "singleton/Router",

    "jsx!views/components/Dialog",
    "jsx!views/components/Dropdown"
], function(
    React,

    Router,

    Dialog,
    Dropdown
) {

    return React.createClass({

        displayName: "Repository",

        getInitialState: function() {
            return {
                showError: false
            };
        },

        render: function() {
            return (
                <tr>
                    { this.renderAnalyzeState() }
                    { this.renderMeasureState() }
                    { this.renderRepoStatus() }

                    <td>
                        { this.props.model.get("kind") }
                    </td>

                    { this.renderRepoLink() }
                    { this.renderRepoActions() }
                    { this.renderActions() }

                    { this.renderErrorModal() }
                </tr>
            );
        },

        renderActions: function() {
            if(this.props.model.get("busy")) {
                return;
            }

            return (
                <td className="actions">
                    { this.renderEdit() }
                    { this.renderPurge() }
                    { this.renderRemove() }
                </td>
            );
        },

        renderEdit: function() {
            return (
                <a
                    href={ "/repository/" + this.props.model.id + "/edit" }
                    className="btn btn-default">

                    <i className="fa fa-edit"></i>
                </a>
            );
        },

        renderPurge: function() {
            return (
                <button className="btn btn-warning" onClick={ this.purge }>
                    <i className="fa fa-folder-o"></i>
                </button>
            );
        },

        purge: function() {
            this.props.model.purge();
        },

        renderRemove: function() {
            return (
                <button className="btn btn-danger" onClick={ this.remove }>
                    <i className="fa fa-remove"></i>
                </button>
            );
        },

        remove: function() {
            this.props.model.destroy();
        },

        renderRepoActions: function() {
            return (
                <td>
                    <div className="btn-group">
                        { this.renderDropdown("Analyze") }
                    </div>
                    <div className="btn-group">
                        { this.renderDropdown("Measure") }
                    </div>
                </td>
            );
        },

        renderDropdown: function(category) {
            if(this.props.model.get("busy")) {
                return this.renderWorkingInfo();
            }

            return (
                <Dropdown
                    title={ category }
                    collection={ this.props.model.get("branches") }
                    renderItem={ this.renderBranch.bind(null, category.toLowerCase()) }
                    onSelect={ this.handleSelect.bind(null, category.toLowerCase()) } />
            );
        },

        handleSelect: function(category, branch) {
            var action = branch.get(category);

            if(!action.interrupted && !action.lastError) {
                branch.perform(category);

                return;
            }

            this.setState({
                resume: branch
            });
        },

        renderBranch: function(category, branch) {
            var action = branch.get(category);

            if(action.finished) {
                return (
                    <span>
                        <i className="fa fa-check"></i>
                        { branch.get("name") }
                    </span>
                );
            }

            if(action.interrupted || branch.lastError) {
                return (
                    <span>
                        <i className="fa fa-warning-sign"></i>
                        { branch.get("name") }
                    </span>
                );
            }

            return (
                <span>
                    <i className="fa fa-blank"></i>
                    { branch.get("name") }
                </span>
            );
        },

        renderWorkingInfo: function() {
            var branch = this.props.model.get("branches").getActiveBranch();

            if(this.props.model.get("status").action === "analyzing") {
                return (
                    <td>
                        { "Analyzing branch " + branch.get("name") }
                    </td>
                );
            }

            return (
                <td>
                    { "Measuring branch " + branch.get("name") }
                </td>
            );
        },

        renderErrorModal: function() {
            if(!this.state.showError) {
                return;
            }

            return (
                <Dialog onRequestHide={ this.toggleError }>
                    { this.props.model.get("error") }
                </Dialog>
            );
        },

        renderError: function() {
            if(!this.props.model.get("error")) {
                return;
            }

            return (
                <a href="#" className="repo-error" onClick={ this.toggleError }>
                    <span className="label label-warning">
                        Attention!
                    </span>
                </a>
            );
        },

        toggleError: function() {
            this.setState({
                showError: !this.state.showError
            });
        },

        renderRepoLink: function() {
            if(this.props.model.get("error")) {
                if(this.props.model.get("busy") || !this.props.model.get("analyzed")) {
                    return (
                        <td>
                            { this.props.model.get("name") }
                            { this.renderError() }
                        </td>
                    );
                }
            }

            return (
                <td>
                    <a href={ "/repository/" + this.props.model.id } onClick={ this.openRepo }>
                        { this.props.model.get("name") }
                    </a>
                    { this.renderError() }
                </td>
            );
        },

        openRepo: function(event) {
            event.preventDefault();

            Router.navigate("/repository/" + this.props.model.id, {
                trigger: true
            });
        },

        renderRepoStatus: function() {
            return (
                <td className="status">
                    { this.renderRepoStatusIcon() }
                </td>
            );
        },

        renderRepoStatusIcon: function() {
            if(!this.props.model.get("anonymous")) {
                return <i className="fa fa-unlock-alt"></i>;
            }

            return <i className="fa fa-lock"></i>;
        },

        renderMeasureState: function() {
            return (
                <td className="status">
                    { this.getStatusIcon({
                        running: this.props.model.get("measuring"),
                        finished: this.props.model.get("measured")
                    })}
                </td>
            );
        },

        renderAnalyzeState: function() {
            return (
                <td className="status">
                    { this.getStatusIcon({
                        running: this.props.model.get("analyzing"),
                        finished: this.props.model.get("analyzed")
                    })}
                </td>
            );
        },

        getStatusIcon: function(status) {
            if(status.running) {
                return this.icon("fa-refresh fa-spin");
            }

            if(status.finished) {
                return this.icon("fa-check");
            }

            return this.icon("fa-question");
        },

        icon: function(cls) {
            cls = cls || "fa-code fa-blank";

            return <i className={"fa " + cls }></i>;
        },
    });

});
