define([
    "react"
], function(
    React
) {

    return React.createClass({

        displayName: "Branch",

        render: function() {
            return (
                <div className="branch">
                    { this.renderHeader() }
                </div>
            );
        },

        renderHeader: function() {
            return (
                <div className='hidden-print'>
                    <table className="table">
                        <thead>
                            <tr>
                                <th colspan='2'>Repository</th>
                                <th colspan='6' className='split'>Branch</th>
                            </tr>
                            <tr>
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
                                <td>{ this.props.model.get("authorCount") }</td>
                                <td className='split'>{ this.props.model.get("name") }</td>
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
    });

});
