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
    $.post("/events/discount/apply", {
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
 * Check if a string is a link
 *
 * @param link
 * @returns {boolean}
 */
function isLink(link) {
    return /^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/.test(link);
}
