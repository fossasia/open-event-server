var $wizardForm = $("#event-wizard-form");

$(document).ready(function () {
    var $wizard = $("#wizard");
    var state = $wizard.data('state');
    var eventId = $wizard.data('id');

    $('a[data-toggle="tab"]').on('show.bs.tab', function (event) {
        return !validate();
    }).on('shown.bs.tab', function (event) {
        var activatedTab = $(event.target);
        history.replaceState(null, null, activatedTab.data("href"));
    });

    $(document).on("click", ".save-event", function () {
        if(!validate()) {
            $wizardForm.submit();
        }
    });

    $(document).on("click", ".publish-unpublish-event", function () {
        if (!validate()) {
            if (state === 'Published') {
                location.href = "/events/" + eventId + "/unpublish/";
            } else {
                var input = $("<input>")
                    .attr("type", "hidden")
                    .attr("name", "state").val("Published");
                $wizardForm.append($(input));
                $wizardForm.submit();
            }
        }
    });

    $(document).on("click", ".next-step", function (e) {
        var $active = $('.wizard .nav-tabs li.active');
        $active.next().removeClass('disabled');
        nextTab($active);
    });

    $(document).on("click", ".prev-step", function (e) {
        var $active = $('.wizard .nav-tabs li.active');
        prevTab($active);
    });

    var highlight = "";
    try {
        highlight = getHashValue('highlight').trim();
    } catch (ignored) {
    }
    if (highlight === "location_name") {
        $wizardForm.find("input[name=location_name]").closest(".form-group").addClass("has-warning");
    }

    if(location.href.indexOf('call-for-speakers') > -1) {
        $("#step-4 > div")[0].scrollIntoView();
    }

    if(location.href.indexOf('form-customization') > -1) {
        $("#step-5 > div")[0].scrollIntoView();
    }


});

function getHashValue(key) {
    var matches = location.hash.match(new RegExp(key + '=([^&]*)'));
    return matches ? matches[1] : null;
}

function validate() {
    try {
        $wizardForm.validator('destroy');
    } catch (ignored) { }

    $wizardForm.validator({
        disable: false,
        feedback: {
            success: 'glyphicon-ok',
            error: 'glyphicon-remove'
        }
    });

    $wizardForm.validator('validate');
    return $wizardForm.data('bs.validator').hasErrors();
}

function nextTab(elem) {
    $(elem).next().find('a[data-toggle="tab"]').click();
}
function prevTab(elem) {
    $(elem).prev().find('a[data-toggle="tab"]').click();
}
