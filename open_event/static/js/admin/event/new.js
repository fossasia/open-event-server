$( document ).ready(function() {
    $('.add-session-type').click(function (){
        var row = "<div class='col-sm-12 row-session-type'>" +
                    "<div class='col-sm-3'>" +
                        "<input type='text' class='form-control' name='session_type[name]' placeholder='Name'>" +
                    "</div>" +
                    "<div class='col-sm-3 input-group'>" +
                        "<input type='text' class='form-control' name='session_type[length]' placeholder='Length'>" +
                        "<span class='input-group-btn'>" +
                            "<button type='button' class='btn btn-danger remove-session-type'>-</button>" +
                        "</span>" +
                    "</div>" +
                "</div>"
        $('.session-types').append(row)

    })

    $( "body" ).on( "click", ".remove-session-type", function (){
        $(this).parent().parent().parent().remove()
    });

    $('.add-social-links').click(function (){
        var row = "<div class='col-sm-12 row-social-links'>" +
                    "<div class='col-sm-3'>" +
                        "<input type='text' class='form-control' name='social[name]' placeholder='Name'>" +
                    "</div>" +
                    "<div class='col-sm-3 input-group'>" +
                        "<input type='text' class='form-control' name='social[length]' placeholder='Length'>" +
                        "<span class='input-group-btn'>" +
                            "<button type='button' class='btn btn-danger remove-social-links'>-</button>" +
                        "</span>" +
                    "</div>" +
                "</div>"
        $('.social-links').append(row)

    })

    $( "body" ).on( "click", ".remove-social-links", function (){
        $(this).parent().parent().parent().remove()
    });

    // Smart Wizard
    $('#wizard').smartWizard({
        labelFinish:'Save Draft',
        onFinish: function(){ $(".event-create-form").submit()}
    });

});
