/**
 * Created by Niranjan (@niranjan94) on 29-May-16.
 *
 * Lot of helper/utility functions used throughout this project
 */

jQuery.fn.extend({
    /**
     * An extended jQuery method to call a callback on an input change
     */
    valueChange: function (callback) {
        return this.each(function () {
            var elem = $(this);
            elem.data('oldVal', elem.val());
            elem.bind("propertychange change click keyup input paste", function (event) {
                if (elem.data('oldVal') != elem.val()) {
                    elem.data('oldVal', elem.val());
                    callback(elem.val(), event, elem);
                }
            });
        });
    },
    /**
     * Append an element at a position
     * @param $element
     * @param index
     * @returns {*}
     */
    appendAt: function ($element, index) {
        return this.each(function () {
            var elem = $(this);
            if (index === 0) {
                elem.prepend($element);
                return;
            } else if (index === -1) {
                elem.append($element);
                return;
            }
            elem.find("div:nth-child(" + (index) + ")").after($element);
        });
    },
    /**
     * Load an object data onto a jQuery element.
     * @param object
     * @param timeParseFormat
     * @returns {*}
     */
    bindObject: function (object, timeParseFormat) {
        return this.each(function () {
            var $elem = $(this);
            $elem.data("object", object);
            _.forOwn(object, function (value, key) {

                if (value.hasOwnProperty("_isAMomentObject") && value._isAMomentObject) {
                    value = value.format(timeParseFormat ? timeParseFormat : "YYYY-MM-DD HH:mm:ss");
                }

                $elem.find('input[name="' + key + '"]').val(value);
                $elem.find('textarea[name="' + key + '"]').text(value);
            });
        });
    },
    /**
     * Disable a jQuery element
     * @returns {*}
     */
    disable: function () {
        return this.each(function () {
            if (!$(this).hasClass("nt")) {
                $(this).addClass("disabled").addClass("processing");
                $(this).attr('disabled', 'disabled');
            }
        });
    },
    /**
     * Enable a jQuery element
     * @returns {*}
     */
    enable: function () {
        return this.each(function () {
            if (!$(this).hasClass("nt")) {
                $(this).removeClass("disabled").removeClass("processing");
                $(this).removeAttr('disabled');
            }
        });
    },
    /**
     * Disable all input,textarea of a form
     * @returns {*}
     */
    lockForm: function () {
        return this.each(function () {
            $(this).find("select,input,textarea,button").disable();
            $(this).find(".note-editable").attr("contenteditable", "false").css("background-color", "#ffffff")

        });
    },
    /**
     * Enable all input, textarea of a form
     * @returns {*}
     */
    unlockForm: function () {
        return this.each(function () {
            $(this).find("select,input,textarea,button").enable();
            $(this).find(".note-editable").attr("contenteditable", "true")
        });
    },
    /**
     * Enable all input, textarea of a form
     * @returns {*}
     */
    setFormLoading: function (isLoading, text) {
        return this.each(function () {
            if (typeof flag === 'undefined') {
                isLoading = true;
            }
            if(isLoading) {
                $(this).lockForm();
                $(this).find("button[type=submit]").html("<i class='fa fa-refresh fa-spin fa-fw'></i> Processing");
            } else {
                $(this).unlockForm();
                $(this).find("button[type=submit]").html(text);
            }
        });
    }

});

/**
 * Extend Lodash and add some additional functionality
 */
if ('undefined' === !typeof _) {
    _.mixin({
        /**
         * Push data into an array while maintaining sort order
         * @param array
         * @param value
         * @param [iteratee=_.identity]
         */
        sortedPush: function (array, value, iteratee) {
            var sortedIndex = _.sortedIndex(array, value, iteratee);
            array.splice(sortedIndex, 0, value);
            return sortedIndex;
        }
    });
}

var cachedFuzzyMatch;
/**
 * Cache the results of a RegExp match.
 * @type {Function}
 */
if ('undefined' === !typeof _) {
    cachedFuzzyMatch = _.memoize(function (pattern) {
        return new RegExp(pattern.split("").reduce(function (a, b) {
            return a + '[^' + b + ']*' + b;
        }), 'i');
    });
}

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
    if (isUndefinedOrNull(multiple)) {
        return val;
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
    if (!offsetAdd) {
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
    try {
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
    } catch (ignored) {
        return false;
    }
}


/**
 * Log an error message to the console
 * @param {string} message The message
 * @param {Object} [ref] a reference object that will be printed along with the message
 */
function logError(message, ref) {
    if (isUndefinedOrNull(ref)) {
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
    if (isUndefinedOrNull(ref)) {
        console.log("[D] " + message);
    } else {
        console.log("[D] " + message + ". Ref ↴");
        console.log(ref);
    }
}

/**
 * Detect if a variable is undefined or null
 * @param {*} variable The variable
 * @returns {boolean} The result of the check
 */
function isUndefinedOrNull(variable) {
    return !!(typeof variable === 'undefined' || variable === null);
}


/**
 * Get the value of a cookie (Original JavaScript code by Chirp Internet: www.chirp.com.au)
 * @param name The name of the cookie
 * @returns {string} the cookie's value
 */
function getCookie(name) {
    var re = new RegExp(name + "=([^;]+)");
    var value = re.exec(document.cookie);
    return (value != null) ? decodeURI(value[1]) : null;
}

/**
 * Recreate a node
 * @param {Node} el the DOM node to be recreated
 * @param {boolean} [withChildren] whether to recreate children too
 */
function recreateNode(el, withChildren) {
    if (withChildren) {
        el.parentNode.replaceChild(el.cloneNode(true), el);
    } else {
        var newEl = el.cloneNode(false);
        while (el.hasChildNodes()) newEl.appendChild(el.firstChild);
        el.parentNode.replaceChild(newEl, el);
    }
}

/**
 * An enhanced file upload button styled using css.
 */
function superFileUploadButton() {
    var inputs = document.querySelectorAll('.upload-btn:not(.no-js)');
    Array.prototype.forEach.call(inputs, function (input) {
        recreateNode(input);
    });
    inputs = document.querySelectorAll('.upload-btn:not(.no-js)');
    Array.prototype.forEach.call(inputs, function (input) {
        var label = input.nextElementSibling,
            labelVal = label.innerHTML;

        input.addEventListener('change', function (e) {
            var fileName = '';
            if (this.files && this.files.length > 1)
                fileName = ( this.getAttribute('data-multiple-caption') || '' ).replace('{count}', this.files.length);
            else
                fileName = e.target.value.split('\\').pop();

            if (fileName)
                label.innerHTML = fileName;
            else
                label.innerHTML = labelVal;
        });
    });
}

/**
 * Split a phrase into words containing only letters
 *
 * From http://stackoverflow.com/a/22075070/1562480 by @rjanjic
 * @param text
 * @returns {Array}
 */
var wordsInText = function (text) {
    var words = [], m, r = /[\u0041-\u005A\u0061-\u007A\u00AA\u00B5\u00BA\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02C1\u02C6-\u02D1\u02E0-\u02E4\u02EC\u02EE\u0370-\u0374\u0376\u0377\u037A-\u037D\u0386\u0388-\u038A\u038C\u038E-\u03A1\u03A3-\u03F5\u03F7-\u0481\u048A-\u0527\u0531-\u0556\u0559\u0561-\u0587\u05D0-\u05EA\u05F0-\u05F2\u0620-\u064A\u066E\u066F\u0671-\u06D3\u06D5\u06E5\u06E6\u06EE\u06EF\u06FA-\u06FC\u06FF\u0710\u0712-\u072F\u074D-\u07A5\u07B1\u07CA-\u07EA\u07F4\u07F5\u07FA\u0800-\u0815\u081A\u0824\u0828\u0840-\u0858\u08A0\u08A2-\u08AC\u0904-\u0939\u093D\u0950\u0958-\u0961\u0971-\u0977\u0979-\u097F\u0985-\u098C\u098F\u0990\u0993-\u09A8\u09AA-\u09B0\u09B2\u09B6-\u09B9\u09BD\u09CE\u09DC\u09DD\u09DF-\u09E1\u09F0\u09F1\u0A05-\u0A0A\u0A0F\u0A10\u0A13-\u0A28\u0A2A-\u0A30\u0A32\u0A33\u0A35\u0A36\u0A38\u0A39\u0A59-\u0A5C\u0A5E\u0A72-\u0A74\u0A85-\u0A8D\u0A8F-\u0A91\u0A93-\u0AA8\u0AAA-\u0AB0\u0AB2\u0AB3\u0AB5-\u0AB9\u0ABD\u0AD0\u0AE0\u0AE1\u0B05-\u0B0C\u0B0F\u0B10\u0B13-\u0B28\u0B2A-\u0B30\u0B32\u0B33\u0B35-\u0B39\u0B3D\u0B5C\u0B5D\u0B5F-\u0B61\u0B71\u0B83\u0B85-\u0B8A\u0B8E-\u0B90\u0B92-\u0B95\u0B99\u0B9A\u0B9C\u0B9E\u0B9F\u0BA3\u0BA4\u0BA8-\u0BAA\u0BAE-\u0BB9\u0BD0\u0C05-\u0C0C\u0C0E-\u0C10\u0C12-\u0C28\u0C2A-\u0C33\u0C35-\u0C39\u0C3D\u0C58\u0C59\u0C60\u0C61\u0C85-\u0C8C\u0C8E-\u0C90\u0C92-\u0CA8\u0CAA-\u0CB3\u0CB5-\u0CB9\u0CBD\u0CDE\u0CE0\u0CE1\u0CF1\u0CF2\u0D05-\u0D0C\u0D0E-\u0D10\u0D12-\u0D3A\u0D3D\u0D4E\u0D60\u0D61\u0D7A-\u0D7F\u0D85-\u0D96\u0D9A-\u0DB1\u0DB3-\u0DBB\u0DBD\u0DC0-\u0DC6\u0E01-\u0E30\u0E32\u0E33\u0E40-\u0E46\u0E81\u0E82\u0E84\u0E87\u0E88\u0E8A\u0E8D\u0E94-\u0E97\u0E99-\u0E9F\u0EA1-\u0EA3\u0EA5\u0EA7\u0EAA\u0EAB\u0EAD-\u0EB0\u0EB2\u0EB3\u0EBD\u0EC0-\u0EC4\u0EC6\u0EDC-\u0EDF\u0F00\u0F40-\u0F47\u0F49-\u0F6C\u0F88-\u0F8C\u1000-\u102A\u103F\u1050-\u1055\u105A-\u105D\u1061\u1065\u1066\u106E-\u1070\u1075-\u1081\u108E\u10A0-\u10C5\u10C7\u10CD\u10D0-\u10FA\u10FC-\u1248\u124A-\u124D\u1250-\u1256\u1258\u125A-\u125D\u1260-\u1288\u128A-\u128D\u1290-\u12B0\u12B2-\u12B5\u12B8-\u12BE\u12C0\u12C2-\u12C5\u12C8-\u12D6\u12D8-\u1310\u1312-\u1315\u1318-\u135A\u1380-\u138F\u13A0-\u13F4\u1401-\u166C\u166F-\u167F\u1681-\u169A\u16A0-\u16EA\u1700-\u170C\u170E-\u1711\u1720-\u1731\u1740-\u1751\u1760-\u176C\u176E-\u1770\u1780-\u17B3\u17D7\u17DC\u1820-\u1877\u1880-\u18A8\u18AA\u18B0-\u18F5\u1900-\u191C\u1950-\u196D\u1970-\u1974\u1980-\u19AB\u19C1-\u19C7\u1A00-\u1A16\u1A20-\u1A54\u1AA7\u1B05-\u1B33\u1B45-\u1B4B\u1B83-\u1BA0\u1BAE\u1BAF\u1BBA-\u1BE5\u1C00-\u1C23\u1C4D-\u1C4F\u1C5A-\u1C7D\u1CE9-\u1CEC\u1CEE-\u1CF1\u1CF5\u1CF6\u1D00-\u1DBF\u1E00-\u1F15\u1F18-\u1F1D\u1F20-\u1F45\u1F48-\u1F4D\u1F50-\u1F57\u1F59\u1F5B\u1F5D\u1F5F-\u1F7D\u1F80-\u1FB4\u1FB6-\u1FBC\u1FBE\u1FC2-\u1FC4\u1FC6-\u1FCC\u1FD0-\u1FD3\u1FD6-\u1FDB\u1FE0-\u1FEC\u1FF2-\u1FF4\u1FF6-\u1FFC\u2071\u207F\u2090-\u209C\u2102\u2107\u210A-\u2113\u2115\u2119-\u211D\u2124\u2126\u2128\u212A-\u212D\u212F-\u2139\u213C-\u213F\u2145-\u2149\u214E\u2183\u2184\u2C00-\u2C2E\u2C30-\u2C5E\u2C60-\u2CE4\u2CEB-\u2CEE\u2CF2\u2CF3\u2D00-\u2D25\u2D27\u2D2D\u2D30-\u2D67\u2D6F\u2D80-\u2D96\u2DA0-\u2DA6\u2DA8-\u2DAE\u2DB0-\u2DB6\u2DB8-\u2DBE\u2DC0-\u2DC6\u2DC8-\u2DCE\u2DD0-\u2DD6\u2DD8-\u2DDE\u2E2F\u3005\u3006\u3031-\u3035\u303B\u303C\u3041-\u3096\u309D-\u309F\u30A1-\u30FA\u30FC-\u30FF\u3105-\u312D\u3131-\u318E\u31A0-\u31BA\u31F0-\u31FF\u3400-\u4DB5\u4E00-\u9FCC\uA000-\uA48C\uA4D0-\uA4FD\uA500-\uA60C\uA610-\uA61F\uA62A\uA62B\uA640-\uA66E\uA67F-\uA697\uA6A0-\uA6E5\uA717-\uA71F\uA722-\uA788\uA78B-\uA78E\uA790-\uA793\uA7A0-\uA7AA\uA7F8-\uA801\uA803-\uA805\uA807-\uA80A\uA80C-\uA822\uA840-\uA873\uA882-\uA8B3\uA8F2-\uA8F7\uA8FB\uA90A-\uA925\uA930-\uA946\uA960-\uA97C\uA984-\uA9B2\uA9CF\uAA00-\uAA28\uAA40-\uAA42\uAA44-\uAA4B\uAA60-\uAA76\uAA7A\uAA80-\uAAAF\uAAB1\uAAB5\uAAB6\uAAB9-\uAABD\uAAC0\uAAC2\uAADB-\uAADD\uAAE0-\uAAEA\uAAF2-\uAAF4\uAB01-\uAB06\uAB09-\uAB0E\uAB11-\uAB16\uAB20-\uAB26\uAB28-\uAB2E\uABC0-\uABE2\uAC00-\uD7A3\uD7B0-\uD7C6\uD7CB-\uD7FB\uF900-\uFA6D\uFA70-\uFAD9\uFB00-\uFB06\uFB13-\uFB17\uFB1D\uFB1F-\uFB28\uFB2A-\uFB36\uFB38-\uFB3C\uFB3E\uFB40\uFB41\uFB43\uFB44\uFB46-\uFBB1\uFBD3-\uFD3D\uFD50-\uFD8F\uFD92-\uFDC7\uFDF0-\uFDFB\uFE70-\uFE74\uFE76-\uFEFC\uFF21-\uFF3A\uFF41-\uFF5A\uFF66-\uFFBE\uFFC2-\uFFC7\uFFCA-\uFFCF\uFFD2-\uFFD7\uFFDA-\uFFDC]+/g;
    while (m = r.exec(text)) {
        words.push(m[0])
    }
    return words;
};

/**
 * Slugify a word.
 * @param text
 * @returns {string}
 */
function partSlugify(text) {
    var words = wordsInText(text);
    for (var index = 0; index < words.length; ++index) {
        words[index] = words[index].toLowerCase();
    }
    return words.join('-');
}

/**
 * Trim text and remove all start and end whitespace
 * @param text
 * @returns {*}
 */
function trimText(text) {
    return text.replace(/^\s\s*/, '').replace(/\s\s*$/, '');
}

/**
 * Slugify a word
 * @param text
 * @returns {string}
 */
function slugify(text) {
    var splitWord = text.split(",");
    for (var index = 0; index < splitWord.length; ++index) {
        splitWord[index] = partSlugify(splitWord[index]);
    }
    return splitWord.join('--');
}

/**
 * Pad a number with zeros
 * @param n
 * @param width
 * @param z
 * @returns {*}
 */
function pad(n, width, z) {
    z = z || '0';
    n = n + '';
    return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;
}
