$(document).ready(function() {

  var counter = 0;
  $('#add-speakers').click(function () {
    var row = '<div class="col-sm-12">' +
                  '<div class=" col-sm-12">' +
                      '<input type="text" class="form-control" name="speakers[email]" placeholder="Email">' +
                  '</div>' +
                  '<div class="col-sm-12 input-group">' +
                      '<span class="input-group-btn">' +
                          '<button type="button" class="btn btn-primary" id="add-speakers">+</button>' +
                      '</span>' +
                  '</div>' +
              '</div>';
    $('.speakers').append(row);
  });

  $( "body" ).on( "click", ".remove-speakers", function () {
    $(this).parent().parent().parent().remove();
  });

  // Smart Wizard
  $("#wizard").smartWizard({
    labelFinish:'Save Draft',
    onFinish: function() { $("#session-create-form").submit(); }
  });

  $('.buttonNext').addClass("btn btn-success");
  $('.buttonPrevious').addClass("btn btn-primary");
  $('.buttonFinish').addClass("btn btn-default");

});
