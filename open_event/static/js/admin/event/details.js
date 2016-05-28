$( document ).ready(function() {
    $('#wizard').smartWizard({
        includeFinishButton:false,
        keyNavigation:false,
        noForwardJumping: true,
    });

    $('.date-picker').daterangepicker({
          singleDatePicker: true,
          timePicker: true,
          calender_style: "picker_4",
          locale: {
            format: 'MM/DD/YYYY h:mm A'
          }
        });

    $("#go_to_call_for_papers").click(function (){
        $('#wizard').smartWizard('goToStep', 2);
//        Send post to change event state to Call for papers
    })

    $("#back_to_draft").click(function (){
        $('#wizard').smartWizard('goToStep', 1);
//        Send post to change event state to Call for papers
    })

    $("#start_scheduling").click(function (){
        $('#wizard').smartWizard('goToStep', 3);
//        Send post to change event state to Call for papers
    })

    $(".actionBar").remove()
});
