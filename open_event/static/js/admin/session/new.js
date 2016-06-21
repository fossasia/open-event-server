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
});
