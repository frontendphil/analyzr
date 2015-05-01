define([
    "react",
    "d3",

    "jsx!views/components/Hint"
], function(
    React,
    d3,

    Hint
) {

    var LANGUAGE_MAPPINGS = {
        "x-java-source": "java",
        "x-java": "java",
        "javascript": "js",
        "x-sql": "sql",
        "x-python": "py",
        "html": "html"
    };

    return React.createClass({

        displayName: "Contributors",

        getInitialState: function() {
            return {
                loading: true,
                page: 1
            };
        },

        componentWillMount: function() {
            this.props.collection.once("sync", function() {
                this.setState({
                    loading: false
                });
            }, this);

            this.props.collection.fetch();
        },

        componentWillUnmount: function() {
            this.props.collection.off(null, null, this);
        },

        render: function() {
            if(this.state.loading) {
                return (
                    <Hint loading={ true }>
                        Loading contributors...
                    </Hint>
                );
            }

            return (
                <div className="contributors">
                    <table className="table table-hover">
                        <thead>
                            <tr>
                                <th className="rank">#</th>
                                <th></th>
                                <th></th>
                                <th>Name</th>
                                <th>First Action</th>
                                <th>Last Action</th>
                                <th>Age</th>
                                <th className="revisions">Revisions</th>
                                <th className="revisions">Rev/Day</th>
                            </tr>
                        </thead>
                        <tbody>
                            { this.props.collection.map(this.renderContributor) }
                        </tbody>
                    </table>
                </div>
            );
        },

        renderContributor: function(contributor, index) {
            var language = "N/A";

            if(contributor.get("primeLanguage")) {
                language = LANGUAGE_MAPPINGS[contributor.get("primeLanguage").mimetype];
            }

            var format = d3.time.format("%d/%m/%Y");

            return (
                <tr>
                    <td className='rank'>{ ((10 * (this.state.page - 1)) + index + 1) }</td>
                    <td className='lang'>{ language }</td>
                    <td className='avatar' style={{ backgroundImage: "url(" + contributor.get("icon") + ")" }}></td>
                    <td className='author'>
                        <a href=' branch + this.view + "'>{ contributor.get("name") }</a>
                    </td>
                    <td>{ format(new Date(contributor.get("firstAction"))) }</td>
                    <td>{ format(new Date(contributor.get("lastAction"))) }</td>
                    <td>{ contributor.get("age") }</td>
                    <td>{ contributor.get("revisions").all }</td>
                    <td>{ contributor.get("workIndex").toFixed(2) }</td>
                </tr>
            );
        }
    });

});
