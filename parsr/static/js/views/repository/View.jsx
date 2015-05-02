define([
    "react",
    "backbone-react-mixin",

    "singleton/Router",

    "jsx!views/repository/BranchSelect",

    "jsx!views/branch/View",

    "jsx!views/components/Hint"
], function(
    React,
    BackboneMixin,

    Router,

    BranchSelect,

    Branch,

    Hint
) {

    return React.createClass({

        displayName: "Repository",

        mixins: [ BackboneMixin ],

        getInitialState: function() {
            return {
                loading: true,
                loadingBranches: true
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

        componentWillUnmount: function() {
            this.props.model.off(null, null, this);
        },

        render: function() {
            if(this.state.loading) {
                return (
                    <Hint loading={ true } view={ true }>
                        <span className="message">
                            Loading Repository...
                        </span>
                    </Hint>
                );
            }

            return (
                <div className="repository container">
                    { this.renderHeader() }
                    { this.renderBranch() }
                </div>
            );
        },

        renderHeader: function() {
            return (
                <div className="view-header">
                    <table className="table">
                        <tbody>
                            <tr>
                                <th>Repository</th>
                                <td>{ this.props.model.get("name") }</td>
                            </tr>
                            <tr>
                                <th>Authors</th>
                                <td>{ this.props.model.get("authorCount") }</td>
                            </tr>
                            <tr>
                                <th>Current branch</th>
                                <td>{ this.renderBranchSelect() }</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            );
        },

        renderBranchSelect: function() {
            return (
                <BranchSelect
                    onSelect={ this.handleBranchSelect }
                    value={ this.props.branch }
                    model={ this.props.model } />
            );
        },

        handleBranchSelect: function(branch) {
            var url = "repository/" + this.props.model.id + "/branch/" + branch.id;

            Router.navigate(url, { trigger: true });
        },

        renderBranch: function() {
            if(!this.props.branch) {
                return (
                    <Hint>
                        Please select a branch
                    </Hint>
                );
            }

            var { branch, ...rest } = this.props;

            return (
                <Branch { ...rest } model={ branch } />
            );
        }
    });

});
