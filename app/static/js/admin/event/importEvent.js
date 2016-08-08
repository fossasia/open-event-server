
function importEventZip(){
    var data = new FormData();
    jQuery.each(jQuery('#import_file')[0].files, function(i, file) {
        data.append('file', file);
    });

    $('#import_status').text('Working...');
    $('#import_error').text('');
    $('#btnImportEvent').prop('disabled', true);
    $('#import_file').prop('disabled', true);
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
            // document.location = '/events/' + data['id'];
            setTimeout(function(){
                importTask(data['task_url']);
            }, 1000);
        },
        error: function(x){
            obj = JSON.parse(x.responseText);
            console.log(obj);
            $('#import_status').text('');
            $('#import_error').text(obj['message']);
        }
    });
}


function importTask(url){
    jQuery.ajax({
        url: url,
        type: 'GET',
        success: function(data){
            console.log(data);
            if (data['state'] != 'SUCCESS'){
                $('#import_status').text('Status: ' + data['state']);
                setTimeout(function(){
                    importTask(url);
                }, 3000);
            } else {
                $('#import_status').text('Status: ' + data['state']);
                document.location = '/events/' + data['result']['id'];
            }
        },
        error: function(x){
            obj = JSON.parse(x.responseText);
            console.log(obj);
            $('#import_status').text('');
            $('#btnImportEvent').prop('disabled', false);
            $('#import_file').prop('disabled', false);
            $('#import_error').text(obj['message']);
        }
    });
}
