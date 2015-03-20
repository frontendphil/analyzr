define([
    "react",
    "backbone-react-mixin",

    "jsx!views/branch/Contributors",
    "jsx!views/branch/Punchcard"
], function(
    React,
    BackboneMixin,

    Contributors,
    Punchcard
) {

    return React.createClass({

        displayName: "Branch",

        mixins: [ BackboneMixin ],

        render: function() {
            return (
                <div className="branch">
                    { this.renderHeader() }

                    <Contributors collection={ this.props.model.get("contributors") } />
                    <Punchcard  model={ this.props.model.get("activity") } />
                </div>
            );
        },

        renderHeader: function() {
            return (
                <div className='hidden-print'>
                    <table className="table">
                        <thead>
                            <tr>
                                <th>Repository</th>
                                <th colSpan='6' className='split'>Branch</th>
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
