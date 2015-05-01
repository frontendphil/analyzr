define([
    "react",
    "backbone-react-mixin",

    "jsx!views/branch/Contributors",
    "jsx!views/branch/Punchcard",
    "jsx!views/branch/Churn",

    "jsx!views/components/Hint"
], function(
    React,
    BackboneMixin,

    Contributors,
    Punchcard,
    Churn,

    Hint
) {

    return React.createClass({

        displayName: "Branch",

        mixins: [ BackboneMixin ],

        getInitialState: function() {
            return {
                loading: true
            };
        },

        componentWillMount: function() {
            this.loadBranch(this.props.model);
        },

        componentWillUnmount: function() {
            this.props.model.off(null, null, this);
        },

        componentWillUpdate: function(nextProps, nextState) {
            if(this.props.model === nextProps.model) {
                return;
            }

            this.props.model.off(null, null, this);

            this.loadBranch(nextProps.model);
        },

        loadBranch: function(branch) {
            this.setState({
                loading: true
            });

            branch.once("sync", function() {
                this.setState({
                    loading: false
                });
            }, this);

            branch.fetch();
        },

        render: function() {
            if(this.state.loading) {
                return (
                    <Hint loading={ true } view={ true }>
                        Loading branch...
                    </Hint>
                );
            }

            return (
                <div className="branch">
                    { this.renderHeader() }
                    { this.renderContent() }
                </div>
            );
        },

        renderHeader: function() {
            return (
                <div className='hidden-print'>
                    <table className="table">
                        <thead>
                            <tr>
                                <th>Branch</th>
                                <th>Last analyzed</th>
                                <th>Last measured</th>
                                <th>Age</th>
                                <th>Authors</th>
                                <th>Author Ratio</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>{ this.props.model.get("name") }</td>
                                <td>{ this.props.model.get("analyze").date }</td>
                                <td>{ this.props.model.get("measure").date }</td>
                                <td>{ this.props.model.get("age") }</td>
                                <td>{ this.props.model.get("authorCount") }</td>
                                <td>{ this.props.model.get("authorRatio") }</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            );
        },

        renderContent: function() {
            return (
                <div className="branch-details">
                    { this.renderAnalyzeResults() }
                    { this.renderMeasurementResults() }
                </div>
            );
        },

        renderAnalyzeResults: function() {
            if(!this.props.model.isAnalyzed()) {
                return (
                    <Hint>
                        The branch has not been analyzed yet
                    </Hint>
                );
            }

            return (
                <div className="analyze-results">
                    <Contributors collection={ this.props.model.get("contributors") } />
                    <Punchcard  model={ this.props.model.get("activity") } />
                </div>
            );
        },

        renderMeasurementResults: function() {
            if(!this.props.model.isMeasured()) {
                return (
                    <Hint>
                        This branch has not been measured yet
                    </Hint>
                );
            }

            return (
                <div className="measure-results">
                    <Churn collection={ this.props.model.get("churn") } />
                </div>
            );
        }
    });

});
