$( document ).ready(function() {
    var counter = 0;
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

    function invite_speakers(evt) {
        var a = $('#invite-speaker-form').serializeArray();
        var email = a[0].value;
        var csrf = $('#csrf_token').val();
        var payload = {
            'email': email,
            'csrf_token': csrf
        };
        var posting = $.ajax({
            type: "POST",
            url: "{{ url_for('invite.create_view', event_id=event.id) }}",
            data: payload
        });

        posting.done(function (result) {
            $('#close-add-track').click();
            new PNotify({
                title: 'Track Added',
                text: 'Track added successfully to DB',
                type: 'success'
            });
        });

        posting.fail(function () {
            $('#close-add-track').click();
            new PNotify({
                title: 'Error',
                text: 'Track could not be added to DB',
                type: 'error'
            });
        });

        return false;
    }

});
