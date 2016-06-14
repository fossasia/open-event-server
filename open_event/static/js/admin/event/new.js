$(document).ready(function() {

  // Smart Wizard
  $("#wizard").smartWizard({
    labelFinish:'Make your event live',
    onFinish: function() {
        var input = $("<input>")
               .attr("type", "hidden")
               .attr("name", "state").val("Published");
        $('#wizard').append($(input));
        $("#event-create-form").submit(); },
    enableAllSteps: true,
  });

  $("#wizard-edit").smartWizard({
    labelFinish:'Make your event live',
    onFinish: function() {
        var input = $("<input>")
               .attr("type", "hidden")
               .attr("name", "state").val("Published");
        $('#wizard-edit').append($(input));
        $("#event-edit-form").submit(); },
    enableAllSteps: true,
   });

  $('.buttonNext').addClass("btn btn-success");
  $('.buttonPrevious').addClass("btn btn-primary");
  $('.buttonFinish').addClass("btn btn-info");
  addSaveButton()

});


function addSaveButton(){
    var wizard = $("#wizard")
    var wizard_edit = $("#wizard-edit")
    if (wizard.length) {
        $("#wizard .buttonFinish").after('<a href="#" id="buttonSave" class="btn btn-warning">Save</a>')
        $("#buttonSave").click(function(){
            $("#event-create-form").submit();
        })
    }
    else if (wizard_edit.length) {
        $("#wizard-edit .buttonFinish").after('<a href="#" id="buttonSave" class="btn btn-warning">Update</a>')
        $("#buttonSave").click(function(){
            $("#event-edit-form").submit();
        })
    }

}
