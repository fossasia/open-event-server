$(document).ready(function () {
    var steps = {
        Draft: 1,
        CallForPapers: 2,
        Published: 3,
        Completed: 4
    };

    var $wizard = $('#wizard');

    $wizard.smartWizard({
        includeFinishButton: false,
        keyNavigation: false,
        noForwardJumping: true,
        onShowStep: handleStepChange
    });

    function handleStepChange($step, context) {
        console.log(context.toStep);
        switch (context.toStep) {
            case steps.Draft:
                // TODO Make a post request to change event state to 'draft'
                break;

            case steps.CallForPapers:
                // TODO Make a post request to change event state to 'Call for papers'
                break;

            case steps.Published:
                // TODO Make a POST request to change event state to 'Published'
                break;

            case steps.Completed:
                // TODO Make a POST request to change event state to 'Completed'

                break;
        }
    }

    $(document).on("click", ".previous-step", function () {
        $wizard.smartWizard('goBackward');
    });

    $(document).on("click", ".next-step", function () {
        $wizard.smartWizard('goForward');
    });

    $(".actionBar").remove();
});
