/**
 * Created by Niranjan on 29-May-16.
 */

/**
 * An extended jQuery method to call a callback on an input change
 */
jQuery.fn.extend({
    valueChange: function (callback) {
        return this.each(function () {
            var elem = $(this);
            elem.data('oldVal', elem.val());
            elem.bind("propertychange change click keyup input paste", function (event) {
                if (elem.data('oldVal') != elem.val()) {
                    elem.data('oldVal', elem.val());
                    callback(elem.val(), event);
                }
            });
        });
    }
});

/**
 * Cache the results of a RegExp match.
 * @type {Function}
 */
var cachedFuzzyMatch = _.memoize(function (pattern) {
    return new RegExp(pattern.split("").reduce(function (a, b) {
        return a + '[^' + b + ']*' + b;
    }), 'i');
});

/**
 * Fuzzy match a string and a pattern/query
 * @param {string} str The target string
 * @param {string} pattern The query string
 * @returns {boolean} true if matches. Else false.
 */
function fuzzyMatch(str, pattern) {
    return cachedFuzzyMatch(pattern).test(str)
}

/**
 * Round of the the closest multiple of a number specified
 * @param {int} val The number to round off
 * @param {int} [multiple=6] The number to whose closest multiple val has to be rounded off to
 * @returns {int}
 */
function roundOffToMultiple(val, multiple) {
    if (!multiple) {
        multiple = 6;
    }
    if (val > 0) {
        var roundUp = Math.ceil(val / multiple) * multiple;
        var roundDown = Math.floor(val / multiple) * multiple;

        if (val >= roundDown + 12) {
            return roundUp;
        } else {
            return roundDown;
        }

    } else {
        return multiple;
    }
}

/**
 * Check if an element is horizontally bound within a parent div
 * @param {jQuery} $parentDiv The parent div
 * @param {jQuery} $childDiv The child div target
 * @param {int} [offsetAdd=0] Offset to add while checking
 * @returns {boolean}
 */
function horizontallyBound($parentDiv, $childDiv, offsetAdd) {
    if(!offsetAdd) {
        offsetAdd = 0;
    }
    var pageWidth = $parentDiv.width();
    var pageHeight = $parentDiv.height();
    var pageTop = $parentDiv.offset().top;
    var pageLeft = $parentDiv.offset().left;
    var elementWidth = $childDiv.width();
    var elementHeight = $childDiv.height();
    var elementTop = $childDiv.offset().top;
    var elementLeft = $childDiv.offset().left;
    var offset = 50 + offsetAdd;
    return !!((elementLeft + offset >= pageLeft) && (elementTop + offset >= pageTop) && (elementLeft + elementWidth <= pageLeft + pageWidth) && (elementTop + elementHeight <= pageTop + pageHeight));
}

/**
 * Borrowed from http://stackoverflow.com/a/5541252/1562480. Author: BC.
 *
 * Check if a div collides/overlaps with/over another div
 *
 * @param {jQuery} $div1 The first div
 * @param {jQuery} $div2 The second div
 * @returns {boolean} true if overlaps/collides, else false.
 */
function collision($div1, $div2) {
    var x1 = $div1.offset().left;
    var y1 = $div1.offset().top;
    var h1 = $div1.outerHeight(true);
    var w1 = $div1.outerWidth(true);
    var b1 = y1 + h1;
    var r1 = x1 + w1;
    var x2 = $div2.offset().left;
    var y2 = $div2.offset().top;
    var h2 = $div2.outerHeight(true);
    var w2 = $div2.outerWidth(true);
    var b2 = y2 + h2;
    var r2 = x2 + w2;
    return !(b1 < y2 || y1 > b2 || r1 < x2 || x1 > r2);
}


/**
 * Log an error message to the console
 * @param {string} message The message
 * @param {Object} [ref] a reference object that will be printed along with the message
 */
function logError(message, ref) {
    if (_.isUndefined(ref)) {
        console.log("[E] " + message);
    } else {
        console.log("[E] " + message + ". Ref ↴");
        console.log(ref);
    }
}

/**
 * Log a debug message to the console
 * @param {string} message The message
 * @param {Object} [ref] a reference object that will be printed along with the message
 */
function logDebug(message, ref) {
    if (_.isUndefined(ref)) {
        console.log("[D] " + message);
    } else {
        console.log("[D] " + message + ". Ref ↴");
        console.log(ref);
    }
}



