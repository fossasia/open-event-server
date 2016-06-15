var $wizardForm = $("#event-wizard-form");

$(document).ready(function () {

    var $wizard = $("#wizard");
    var wizardType = $wizard.data("type");

    // Smart Wizard
    $wizard.smartWizard({
        labelFinish: 'Make your event live',
        onFinish: function () {
            var input = $("<input>")
                .attr("type", "hidden")
                .attr("name", "state").val("Published");
            $wizard.append($(input));
            $wizardForm.submit();
        },
        enableAllSteps: true,
        onLeaveStep: onLeaveStep
    });

    $('.buttonNext').addClass("btn btn-success");
    $('.buttonPrevious').addClass("btn btn-primary");
    $('.buttonFinish').addClass("btn btn-info");

    $wizard.find(".buttonFinish")
        .after('<a href="#" id="buttonSave" class="btn btn-warning">' + (wizardType === 'create' ? 'Save' : 'Update') + '</a>');

    $("#buttonSave").click(function () {
        $wizardForm.submit();
    })


});

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
