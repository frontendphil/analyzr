define([
    "react",
    "backbone-react-mixin",

    "singleton/Router",

    "jsx!views/branch/View",

    "jsx!views/components/Hint"
], function(
    React,
    BackboneMixin,

    Router,

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

                this.props.model.get("branches").fetch();
            }, this);

            this.props.model.get("branches").once("sync", function() {
                this.setState({
                    loadingBranches: false
                });

                if(this.props.branchId) {
                    return;
                }

                var branch = this.props.model.getMostInterestingBranch();

                Router.navigate("/repository/" + this.props.model.id + "/branch/" + branch.id, {
                    trigger: true,
                    replace: true
                });
            }, this);

            this.props.model.fetch();
        },

        render: function() {
            if(this.state.loading) {
                return (
                    <Hint loading={ true } view={ true }>
                        <span className="message">
                            Loading...
                        </span>
                    </Hint>
                );
            }

            if(this.state.loadingBranches) {
                return (
                    <Hint loading={ true } view={ true }>
                        Loading Branches...
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
                    <h1>{ this.props.model.get("name") }</h1>
                </div>
            );
        },

        getBranch: function() {
            return this.props.model.get("branches").get(this.props.branchId);
        },

        renderBranch: function() {
            var branch = this.getBranch();

            if(!branch) {
                return (
                    <Hint>
                        No branches have been analyzed or measured.
                    </Hint>
                );
            }

            return (
                <Branch model={ branch } />
            );
        }
    });

});
