var $wizardForm = $("#event-wizard-form");

$(document).ready(function () {

    var $wizard = $("#wizard");
    var state = $wizard.data('state');
    var eventId = $wizard.data('id');

    // Smart Wizard
    $wizard.smartWizard({
        labelFinish: 'Make your event live',
        onFinish: function () {
            if (state === 'Published') {
                location.href = "/events/" + eventId + "/unpublish/";
            } else {
                var input = $("<input>")
                    .attr("type", "hidden")
                    .attr("name", "state").val("Published");
                $wizard.append($(input));
                $wizardForm.submit();
            }
        },
        enableAllSteps: true,
        onLeaveStep: onLeaveStep
    });

    $('.buttonNext').addClass("btn btn-success");
    $('.buttonPrevious').addClass("btn btn-primary");
    $('.buttonFinish').addClass("btn btn-info");

    $wizard.find(".buttonFinish")
        .after('<a href="#" id="buttonSave" class="btn btn-warning">Save</a>');

    if (state === 'Published') {
        $wizard.find(".buttonFinish").text("Unpublish").removeClass("btn-info").addClass("btn-danger");
    }

    $("#buttonSave").click(function () {
        $wizardForm.submit();
    });

    var hash = "";
    try {
        hash = getHashValue('step').trim();
    } catch (ignored) {
    }

    if (hash !== "1" && hash !== "location_name") {
        $wizard.smartWizard('goToStep', parseInt(hash));
    } else if (hash === "location_name") {
        $wizardForm.find("input[name=location_name]").closest(".form-group").addClass("has-warning");
    }

    $(window).resize(function () {
        $wizard.smartWizard('fixHeight');
    });
});

function getHashValue(key) {
    var matches = location.hash.match(new RegExp(key + '=([^&]*)'));
    return matches ? matches[1] : null;
}

function onLeaveStep(obj, context) {
    return !validate();
}

function validate() {
    try {
        $wizardForm.validator('destroy');
    } catch (ignored) {
    }

    $wizardForm.validator({
        disable: false,
        feedback: {
            success: 'glyphicon-ok',
            error: 'glyphicon-remove'
        }
    });

    $wizardForm.validator('validate');
    return $wizardForm.data('bs.validator').hasErrors()
}
