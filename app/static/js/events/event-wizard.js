$(window).on('load', function () {
    var $wizard = $("#wizard");
    var highlight = "";
    try {
        highlight = getHashValue("highlight").trim();
    } catch (ignored) { }
    if (highlight === "location_name") {
        $wizard.find("input[name=location_name]").closest(".form-group").addClass("has-warning");
    }

    if (location.hash.indexOf("call-for-speakers") > -1) {
        $("#step-4").find("div")[0].scrollIntoView();
    }

    if (location.hash.indexOf("form-customization") > -1) {
        $("#step-5").find("div")[0].scrollIntoView();
    }
});

function getHashValue(key) {
    var matches = location.hash.match(new RegExp(key + "=([^&]*)"));
    return matches ? matches[1] : null;
}
