define([
    "react",

    "views/mixins/DropDownMixin",

    "jsx!views/repository/BranchSelectItem",

    "jsx!views/components/DropDown",
    "jsx!views/components/Hint"
], function(
    React,

    DropDownMixin,

    BranchSelectItem,

    DropDown,
    Hint
) {

    return React.createClass({

        displayName: "BranchSelect",

        mixins: [ DropDownMixin ],

        render: function() {
            return (
                <div className="branch-select">
                    <DropDown
                        open={ this.state.open }
                        onToggle={ this.toggle }
                        toggle={ this.renderToggle() }>

                        { this.renderBranches() }
                    </DropDown>
                </div>
            );
        },

        renderBranches: function() {
            if(!this.state.open) {
                return;
            }

            return this.props.model.get("branches").map(this.renderBranch);
        },

        renderBranch: function(branch) {
            return <BranchSelectItem onClick={ this.handleSelect.bind(null, branch) } model={ branch } />;
        },

        handleSelect: function(branch) {
            this.props.onSelect(branch);

            this.close();
        },

        renderToggle: function() {
            return (
                <button className="btn btn-default btn-sm">
                    { this.getTitle() }
                    <i className="icon icon-menu" />
                </button>
            );
        },

        getTitle: function() {
            if(!this.props.value) {
                return (
                    <Hint inline={ true }>
                        No branch selected
                    </Hint>
                );
            }

            return this.props.value.get("name");
        }

    });

});
