
function importEventZip(){
    var data = new FormData();
    jQuery.each(jQuery('#import_file')[0].files, function(i, file) {
        data.append('file', file);
    });

    jQuery.ajax({
        url: '/api/v2/events/import/json',
        data: data,
        cache: false,
        contentType: false,
        processData: false,
        type: 'POST',
        success: function(data){
            console.log(data);
            // redirect to created event
            document.location = '/events/' + data['id'];
        },
        error: function(x){
            obj = JSON.parse(x.responseText);
            console.log(obj);
            $('#import_error').text(obj['message']);
        }
    });
}
