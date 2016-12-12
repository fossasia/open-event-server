var $wizardForm = $("#event-wizard-form");

$(document).ready(function () {

    $("a[data-toggle=tab]").on("shown.bs.tab", function (event) {
        var activatedTab = $(event.target);
        history.replaceState(null, null, activatedTab.data("href"));
    });

    $(document).on("click", ".next-step", function (e) {
        var $active = $(".wizard .nav-tabs li.active");
        $active.next().removeClass("disabled");
        nextTab($active);
    });

    $(document).on("click", ".prev-step", function (e) {
        var $active = $(".wizard .nav-tabs li.active");
        prevTab($active);
    });

    var highlight = "";
    try {
        highlight = getHashValue("highlight").trim();
    } catch (ignored) {
    }
    if (highlight === "location_name") {
        $wizardForm.find("input[name=location_name]").closest(".form-group").addClass("has-warning");
    }

    if (location.href.indexOf("call-for-speakers") > -1) {
        $("#step-4").find("div")[0].scrollIntoView();
    }

    if (location.href.indexOf("form-customization") > -1) {
        $("#step-5").find("div")[0].scrollIntoView();
    }
});

function getHashValue(key) {
    var matches = location.hash.match(new RegExp(key + "=([^&]*)"));
    return matches ? matches[1] : null;
}

function nextTab(elem) {
    $(elem).next().find("a[data-toggle=tab]").click();
}
function prevTab(elem) {
    $(elem).prev().find("a[data-toggle=tab]").click();
}
