/**
 * Created by niranjan94 on 28-Jul-16.
 */

var handler = StripeCheckout.configure({
    key: window.stripe_publishable_key,
    locale: 'auto',
    name: 'Open Event',
    amount: window.order_amount,
    description: window.event_name + ' tickets',
    token: function (token) {
        // You can access the token ID with `token.id`.
        // Get the token ID to your server-side code for use.
    }
});

window.order_created_at = moment(window.order_created_at);
window.order_expires_at = window.order_created_at.clone();
window.order_expires_at.add(10, 'minutes');

var $timeLeft = $("#time-left");

function pad(n, width, z) {
    z = z || '0';
    n = n + '';
    return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;
}

var shownExpired = false;
function executeOrderExpired() {
    if (!shownExpired) {
        shownExpired = true;
        $.post(window.expire_url, {}, function () {
            location.href = window.expired_redirect;
        });
        alert("You have exceeded the time limit and your reservation has been released. We apologize for the inconvenience.");
    }
}

setInterval(function () {
    var now = moment();
    var diff = window.order_expires_at.diff(now, 'seconds');
    if (diff >= 0) {
        var duration = moment.duration(diff, 'seconds');
        $timeLeft.text(pad(duration.minutes(), 2) + ":" + pad(duration.seconds(), 2));
    } else {
        executeOrderExpired();
    }

}, 1000);

var $orderPaymentForm = $("#order-payment-form");
var $payViaStripe = $('#pay-via-stripe');
var userEmail = '';

$orderPaymentForm.submit(function (e) {
    e.preventDefault();
    var data = $orderPaymentForm.serialize();
    $orderPaymentForm.lockForm();
    $.ajax({
        url: $orderPaymentForm.attr('action'),
        type: 'post',
        dataType: 'json',
        data: data,
        success: function (json) {
            if(json.status == "ok") {
                userEmail = json.email;
                $payViaStripe.click();
            } else {
                
            }

        }
    });
});


$payViaStripe.on('click', function (e) {
    handler.open({
        amount: window.order_amount,
        email: userEmail
    });
    e.preventDefault();
});

$(window).on('popstate', function () {
    handler.close();
});
