var Utils;

(function() {

    if(!String.prototype.capitalize) {
        String.prototype.capitalize = function() {
            if(!this) {
                return "";
            }

            var firstLetter = this.slice(0, 1);

            return firstLetter.toUpperCase() + this.slice(1);
        };
    }

}());
