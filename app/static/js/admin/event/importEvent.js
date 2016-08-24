
function importEventZip(){
    var data = new FormData();
    jQuery.each(jQuery('#import_file')[0].files, function(i, file) {
        data.append('file', file);
    });

    $('#import_status').text('Uploading file.. Please don\'t close this window');
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
                $('#import_status').html('<b>Status:</b> ' + data['state']);
                setTimeout(function(){
                    importTask(url);
                }, 3000);
            } else {
                $('#import_status').html('<b>Status:</b> ' + data['state']);
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


function importTaskTable(task, field_id){
    console.log(task);
    url = '/api/v2/tasks/' + task;
    jQuery.ajax({
        url: url,
        type: 'GET',
        success: function(data){
            console.log(data);
            if (data['state'] == 'PENDING'){ // task is lost
                $(field_id).html('Failed');
                return;
            }
            if (data['state'] != 'SUCCESS'){
                $(field_id).html('<b>Status:</b> ' + data['state']);
                setTimeout(function(){
                    importTaskTable(task, field_id);
                }, 3000);
            } else {
                $(field_id).html('<b>Status:</b> ' + data['state']);
            }
        },
        error: function(x){
            console.log(x.responseText);
            obj = JSON.parse(x.responseText);
            $(field_id).text(obj['message']);
        }
    });
}
