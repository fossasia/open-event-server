/**
 * Created by niranjan94 on 28-Jul-16.
 */
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
