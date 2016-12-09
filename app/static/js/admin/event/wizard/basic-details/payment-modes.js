var $stripeConnectedMessage = $("#stripe-connected-message");
$(".stripe-connect").click(function (e) {
    e.preventDefault();
    $.oauthpopup({
        path: "https://connect.stripe.com/oauth/authorize?response_type=code&client_id={{ key_settings.stripe_client_id }}&scope=read_write&redirect_uri={{ url_for('ticketing.stripe_callback', _external=true) }}",
        callback: function () {
            // Disallow test accounts. Only accept live accounts.
            if (window.oauth_response.live_mode) {
                $("input[name=stripe_added]").val("yes");
                $stripeConnectedMessage.find("input[name=stripe_secret_key]").val(window.oauth_response.access_token);
                $stripeConnectedMessage.find("input[name=stripe_refresh_token]").val(window.oauth_response.refresh_token);
                $stripeConnectedMessage.find("input[name=stripe_publishable_key]").val(window.oauth_response.stripe_publishable_key);
                $stripeConnectedMessage.find("input[name=stripe_user_id]").val(window.oauth_response.stripe_user_id);
                $stripeConnectedMessage.find("input[name=stripe_email]").val(window.oauth_response.email);
                $stripeConnectedMessage.find(".stripe-email").text(window.oauth_response.email);
                $stripeConnectedMessage.show();
                $(".stripe-connect").hide();
            } else {
                createSnackbar('Your stripe account is not live. Only live accounts can be used for collecting payments.')
            }
        }
    });

});

$(".stripe-delink").click(function (e) {
    e.preventDefault();
    $("input[name=stripe_added]").val("no");
    $stripeConnectedMessage.hide();
    $stripeConnectedMessage.find("input").val("");
    $stripeConnectedMessage.find(".stripe-email").text("");
    $(".stripe-connect").show();
});

var $paypalHolder = $("#paypal-holder");
$("#pay_by_paypal").change(function () {
    if ($("#pay_by_paypal").is(":checked"))
        $paypalHolder.fadeIn();
    else
        $paypalHolder.fadeOut();
});

var $stripeHolder = $("#stripe-holder");
$("#pay_by_stripe").change(function () {
    if ($("#pay_by_stripe").is(":checked"))
        $stripeHolder.fadeIn();
    else
        $stripeHolder.fadeOut();
});

$("select[name=payment_currency]").change(function () {
    var $selected = $(this).find(":selected");
    if ($selected.data("has-paypal") !== "True") {
        $("#paypal-gateway").fadeOut().find("input").prop("checked", false).val("");
    } else {
        $("#paypal-gateway").fadeIn();
    }
    if ($selected.data("has-stripe") !== "True") {
        $("#stripe-gateway").fadeOut().find("input").prop("checked", false).val("");
    } else {
        $("#stripe-gateway").fadeIn();
    }
}).trigger('change');

var $chequeHolder = $("#cheque-instuctions-holder");
$("#pay_by_cheque").change(function () {
    if ($("#pay_by_cheque").is(":checked"))
        $chequeHolder.fadeIn();
    else
        $chequeHolder.fadeOut();
});

var $bankHolder = $("#bank-instuctions-holder");
$("#pay_by_bank").change(function () {
    if ($("#pay_by_bank").is(":checked"))
        $bankHolder.fadeIn();
    else
        $bankHolder.fadeOut();
});

var $onsiteHolder = $("#onsite-instuctions-holder");
$("#pay_onsite").change(function () {
    if ($("#pay_onsite").is(":checked"))
        $onsiteHolder.fadeIn();
    else
        $onsiteHolder.fadeOut();
});
