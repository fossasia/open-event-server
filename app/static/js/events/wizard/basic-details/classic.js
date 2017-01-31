/**
 * Start stripe OAuth flow
 *
 * @param callback
 */
function stripeConnect(callback) {
    $.oauthpopup({
        path: window.stripeConnectUrl,
        callback: function () {
            // Disallow test accounts. Only accept live accounts.
            if (_.isUndefined(window.oauth_response)) {
                callback(false);
            } else {
                if (window.oauth_response.live_mode) {
                    callback(true, window.oauth_response);
                } else {
                    createSnackbar('Your stripe account is not live. Only live accounts can be used for collecting payments.');
                    callback(false);
                }
            }
        }
    });
}

/**
 * Apply a discount code
 *
 * @param discountCodeValue
 * @param callback
 */
function applyDiscountCode(discountCodeValue, callback) {
    $.post("/events/discount/apply/", {
        discount_code: discountCodeValue
    }).done(function (data) {
        if (data.status === 'ok') {
            callback(data.discount_code.id, data.discount_code.value + "% over a period of " + data.discount_code.max_quantity + " month(s)");
        } else {
            var message = "An error occurred while trying to apply the discount code.";
            if (data.hasOwnProperty('message')) {
                message = data.message;
            }
            callback(null, message);
        }
    }).fail(function () {
        callback(null, "An error occurred while trying to apply the discount code.");
    });
}

/**
 * @type {RegExp}
 */
var urlRe = new RegExp(
  "^" +
    // protocol identifier
    "(?:(?:https?)://)" +
    // user:pass authentication
    "(?:\\S+(?::\\S*)?@)?" +
    "(?:" +
      // IP address exclusion
      // private & local networks
      "(?!(?:10|127)(?:\\.\\d{1,3}){3})" +
      "(?!(?:169\\.254|192\\.168)(?:\\.\\d{1,3}){2})" +
      "(?!172\\.(?:1[6-9]|2\\d|3[0-1])(?:\\.\\d{1,3}){2})" +
      // IP address dotted notation octets
      // excludes loopback network 0.0.0.0
      // excludes reserved space >= 224.0.0.0
      // excludes network & broacast addresses
      // (first & last IP address of each class)
      "(?:[1-9]\\d?|1\\d\\d|2[01]\\d|22[0-3])" +
      "(?:\\.(?:1?\\d{1,2}|2[0-4]\\d|25[0-5])){2}" +
      "(?:\\.(?:[1-9]\\d?|1\\d\\d|2[0-4]\\d|25[0-4]))" +
    "|" +
      // host name
      "(?:(?:[a-z\\u00a1-\\uffff0-9]-*)*[a-z\\u00a1-\\uffff0-9]+)" +
      // domain name
      "(?:\\.(?:[a-z\\u00a1-\\uffff0-9]-*)*[a-z\\u00a1-\\uffff0-9]+)*" +
      // TLD identifier
      "(?:\\.(?:[a-z\\u00a1-\\uffff]{2,}))" +
      // TLD may end with dot
      "\\.?" +
    ")" +
    // port number
    "(?::\\d{2,5})?" +
    // resource path
    "(?:[/?#]\\S*)?" +
  "$", "i"
);

/**
 * Check if a string is a link
 *
 * @param link
 * @returns {boolean}
 */
function isLink(link) {
    return urlRe.test(link);
}
