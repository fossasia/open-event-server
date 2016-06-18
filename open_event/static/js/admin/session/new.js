var $wizardForm = $("#session-create-form");
$(document).ready(function() {

  var counter = 0;
  $('#add-speakers').click(function () {
    var row = '<div class="item form-group">'+
              '<label class="control-label">Email </label>'+
                '<div class="">'+
                    '<input type="text" class="form-control col-md-7 col-sm-7" name="speakers[email]" placeholder="Email Address of Speaker" style="width:60%;">'+
                '</div>'+
                '<div class="col-sm-1 col-md-1 input-group">'+
                    '<span class="input-group-btn">'+
                        '<button type="button" class="btn btn-danger" id="remove-speakers">-</button>'+
                    '</span>'+
                 '</div>'+
                '</div>';
    $('.speakers').append(row);
  });

  $( "body" ).on( "click", "#remove-speakers", function () {
    $(this).parent().parent().parent().remove();
  });

  // Smart Wizard
  $("#wizard").smartWizard({
    labelFinish:'Save Draft',
    onFinish: function() { $("#session-create-form").submit(); },
    enableAllSteps: true,
    onLeaveStep: onLeaveStep
  });

  $('.buttonNext').addClass("btn btn-success");
  $('.buttonPrevious').addClass("btn btn-primary");
  $('.buttonFinish').addClass("btn btn-default");

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
    return $wizardForm.data('bs.validator').hasErrors();
}

