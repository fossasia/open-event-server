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
                    callback(elem.val(), event);
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
 * A simple function to create a material design Snackbar with an action button
 * @param {string} message The message to be displayed
 * @param {string} [actionText=Dismiss] The action text to be displayed
 * @param {callback} [action] The callback to execute when pressing the action button
 * @param {number} [delay=5000] The delay for the snackbar
 */
var createSnackbar = (function () {
    var previous = null;

    /**
     *
     */
    return function (message, actionText, action, delay) {
        if (previous) {
            previous.dismiss();
        }

        if (typeof actionText === 'undefined' || actionText == null) {
            actionText = "Dismiss";
        }

        if (typeof delay === 'undefined' || delay == null) {
            delay = 5000;
        }
        var snackbar = document.createElement('div');
        snackbar.className = 'paper-snackbar';
        snackbar.dismiss = function () {
            this.style.opacity = 0;
        };
        var text = document.createTextNode(message);
        snackbar.appendChild(text);
        if (actionText) {
            var hasAction = true;
            if (!action) {
                action = snackbar.dismiss.bind(snackbar);
                hasAction = false;
            }
            var actionButton = document.createElement('button');
            actionButton.className = 'action';
            actionButton.innerHTML = actionText;
            if (hasAction) {
                actionButton.addEventListener('click', function () {
                    action();
                    snackbar.dismiss.bind(snackbar);
                });
            } else {
                actionButton.addEventListener('click', action);
            }

            snackbar.appendChild(actionButton);
        }
        setTimeout(function () {
            if (previous === this) {
                previous.dismiss();
            }
        }.bind(snackbar), delay);

        snackbar.addEventListener('transitionend', function (event, elapsed) {
            if (event.propertyName === 'opacity' && this.style.opacity == 0) {
                window.snackbar_elapsed = elapsed;
                this.parentElement.removeChild(this);
                if (previous === this) {
                    previous = null;
                }
            }
        }.bind(snackbar));

        previous = snackbar;
        document.body.appendChild(snackbar);
        window.snackbar_bottom = getComputedStyle(snackbar).bottom;
        snackbar.style.bottom = '0px';
        snackbar.style.left = '0px';
        snackbar.style.opacity = 1;
    };
})();

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
 * Slugify a word.
 * @param text
 * @returns {string}
 */
function partSlugify(text) {
    return text.toString().toLowerCase()
        .replace(/\s+/g, '-')           // Replace spaces with -
        .replace(/[^\w\-]+/g, '')       // Remove all non-word chars
        .replace(/\-\-+/g, '-')         // Replace multiple - with single -
        .replace(/^-+/, '')             // Trim - from start of text
        .replace(/-+$/, '');            // Trim - from end of text
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
