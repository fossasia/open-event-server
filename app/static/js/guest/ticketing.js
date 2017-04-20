/**
 * Created by niranjan94 on 28-Jul-16.
 */

window.token_recieved = false;
if(window.pay_by_stripe == "True" && window.order_amount > 0){
   var handler = StripeCheckout.configure({
        key: window.stripe_publishable_key,
        locale: 'auto',
        name: 'Open Event',
        amount: window.order_amount,
        currency: window.currency,
        description: window.event_name + ' tickets',
        token: function (token) {
            window.token_recieved = true;
            chargeOrderPayment(token.id);
        },
        closed: function () {
            if (window.token_recieved) {
                window.token_recieved = false;
            } else {
                createSnackbar("The payment was cancelled. Processing ...");
                setTimeout(function () {
                    location.reload(true);
                }, 1000);
            }
        }
    });
}


window.order_created_at = moment.utc(window.order_created_at);
window.order_expires_at = window.order_created_at.clone();
window.order_expires_at.add(10, 'minutes');

var $registrationInformationHolder = $("#registration-information-holder");
var $timeLeft = $("#time-left");

function pad(n, width, z) {
    z = z || '0';
    n = n + '';
    return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;
}

if (!window.from_organzier) {
    var shownExpired = false;

    function executeOrderExpired() {
        if (!shownExpired) {
            shownExpired = true;
            $("#registration-information-holder").fadeOut();
            $.post(window.expire_url, {}, function () {
                location.href = window.expired_redirect;
            });
            alert("You have exceeded the time limit and your reservation has been released. We apologize for the inconvenience.");
        }
    }

    setInterval(function () {
        if (typeof window.stop_timer === 'undefined' || window.stop_timer !== 'right_away') {
            var now = moment.utc();
            var diff = window.order_expires_at.diff(now, 'seconds');
            if (diff >= 0) {
                var duration = moment.duration(diff, 'seconds');
                $timeLeft.text(pad(duration.minutes(), 2) + ":" + pad(duration.seconds(), 2));
            } else {
                executeOrderExpired();
            }
        }
    }, 1000);

}

var $orderPaymentForm = $("#order-payment-form");
var $submitButton = $('#submitButton');
var $payViaStripe = $('#pay-via-stripe');
var userEmail = '';

$orderPaymentForm.submit(function (e) {
    e.preventDefault();
    $orderPaymentForm.validator('validate');
    if($submitButton.hasClass('disabled'))
    {
        return false;
    }
    var data = $orderPaymentForm.serialize();
    $orderPaymentForm.setFormLoading();

    $.ajax({
        url: $orderPaymentForm.attr('action'),
        type: 'post',
        dataType: 'json',
        data: data,
        success: function (json) {
            $('html, body').animate({scrollTop: 0}, 'slow');
            if (json.status === "ok") {
                if (json.hasOwnProperty('email')) {
                    userEmail = json.email;
                }

                switch (json.action) {
                    case "show_completed":
                        createSnackbar("Your payment was a success. Redirecting ...");
                        setTimeout(function () {
                            location.reload(true);
                        }, 1000);
                        window.stop_timer = "right_away";
                        $registrationInformationHolder.fadeOut();
                        break;
                    case "start_stripe":
                        $payViaStripe.click();
                        break;
                    case "start_paypal":
                        createSnackbar("Redirecting you to PayPal to complete the payment...");
                        $registrationInformationHolder.fadeOut();
                        location.href = json.redirect_url;
                        break;
                    default:
                        $orderPaymentForm.setFormLoading(false, 'Pay now');
                        createSnackbar("An error occurred while initializing your payment.", "Try again", function () {
                            $orderPaymentForm.submit();
                        });
                        break;
                }

            } else {
                $orderPaymentForm.setFormLoading(false, 'Pay now');
                createSnackbar("An error occurred while initializing your payment.", "Try again", function () {
                    $orderPaymentForm.submit();
                });
            }

        }
    });
});

function chargeOrderPayment(tokenId) {
    var data = {
        stripe_token_id: tokenId,
        identifier: window.order_identifier
    };
    $.ajax({
        url: window.stripe_charge_at,
        type: 'post',
        dataType: 'json',
        data: data,
        success: function (json) {
            if (json.status === "ok") {
                userEmail = json.email;
                createSnackbar("Your payment was a success. Redirecting ...");
                setTimeout(function () {
                    location.reload(true);
                }, 1000);
                window.stop_timer = "right_away";
                $("#registration-information-holder").fadeOut();

            } else {
                createSnackbar("An error occurred while processing your payment.", "Try again", function () {
                    chargeOrderPayment(tokenId);
                });
            }
        },
        error: function () {
            createSnackbar("An error occurred while processing your payment.", "Try again", function () {
                chargeOrderPayment(tokenId);
            });
        }
    });
}

$payViaStripe.on('click', function (e) {
    handler.open({
        amount: window.order_amount * 100,
        email: userEmail
    });
    e.preventDefault();
});

$(window).on('popstate', function () {
    handler.close();
});

var checked = false;
var checkboxes =  $('.autofill-checkbox');
checkboxes.click(function(){
        var firstName = $('#firstname').val();
        var lastname =  $('#lastname').val();
        var email =     $('#email').val();
        var requiredId = this.id;
        checkboxes.prop('disabled', true);
        $(this).prop('disabled', false);
        if($(this).is(':checked')) {
            $('#' + requiredId + '-holders\\[firstname\\]').val(firstName);
            $('#' + requiredId + '-holders\\[lastname\\]').val(lastname);
            $('#' + requiredId + '-holders\\[email\\]').val(email);
        }
        else {
            $('#' + requiredId + '-holders\\[firstname\\]').val("");
            $('#' + requiredId + '-holders\\[lastname\\]').val("");
            $('#' + requiredId + '-holders\\[email\\]').val("");
            checkboxes.prop('disabled', false );
        }
});

