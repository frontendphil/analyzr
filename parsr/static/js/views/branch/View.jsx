define([
    "react"
], function(
    React
) {

    return React.createClass({

        displayName: "Branch",

        getInitialState: function() {
            return {
                loading: true
            };
        },

        componentDidMount: function() {
            this.props.model.once("sync", function() {
                var repo = this.props.model.get("repository");

                repo.once("sync", function() {
                    this.setState({
                        loading: false
                    });
                }, this);

                repo.fetch();
            }, this);

            this.props.model.fetch();
        },

        render: function() {
            return (
                <div className="branch">
                    { this.renderHeader() }
                </div>
            );
        },

        renderHeader: function() {
            if(this.state.loading) {
                return;
            }

            return (
                <div className='container hidden-print'>
                    <table className="table">
                        <thead>
                            <tr>
                                <th colspan='2'>Repository</th>
                                <th colspan='6' className='split'>Branch</th>
                            </tr>
                            <tr>
                                <th>Branches</th>
                                <th>Authors</th>
                                <th className='split'>Name</th>
                                <th>Last analyzed</th>
                                <th>Last measured</th>
                                <th>Age</th>
                                <th>Authors</th>
                                <th>Author Ratio</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>{ this.props.model.repository.get("branchCount") }</td>
                                <td>{ this.props.model.get("authorCount") }</td>
                                <td className='split'>{ branch.get("name") }</td>
                                <td>{ branch.get("analyze").date }</td>
                                <td>{ branch.get("measure").date }</td>
                                <td>{ branch.get("age") }</td>
                                <td>{ branch.get("authorCount") }</td>
                                <td>{ branch.get("authorRatio") }</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            );
        },
    });

});
