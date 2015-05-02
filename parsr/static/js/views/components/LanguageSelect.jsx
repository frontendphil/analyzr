define([
    "react",

    "views/mixins/DropDownMixin",

    "jsx!views/components/DropDown",
    "jsx!views/components/Hint"
], function(
    React,

    DropDownMixin,

    DropDown,
    Hint
) {

    return React.createClass({

        displayName: "LanguageSelect",

        mixins: [ DropDownMixin ],

        render: function() {
            return (
                <div className="language-select">
                    <DropDown
                        open={ this.state.open }
                        onToggle={ this.toggle }
                        toggle={ this.renderToggle() }>

                        { this.renderLanguages() }
                    </DropDown>
                </div>
            );
        },

        renderToggle: function() {
            return (
                <button className="btn btn-default">
                    { this.renderTitle() }
                    <i className="icon icon-speech-bubble" />
                </button>
            );
        },

        renderTitle: function() {
            if(!this.props.value) {
                return (
                    <Hint inline={ true }>
                        No language selected
                    </Hint>
                );
            }

            return this.props.value;
        },

        renderLanguages: function() {
            if(!this.state.open) {
                return;
            }

            return this.props.collection.map(this.renderLanguage);
        },

        renderLanguage: function(language) {
            return (
                <div className="language" onClick={ this.handleSelect.bind(null, language) }>
                    <i className="icon icon-speech-bubble" />
                    { language }
                </div>
            );
        },

        handleSelect: function(language) {
            this.props.onSelect(language);

            this.close();
        }
    });

});
