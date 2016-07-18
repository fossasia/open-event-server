// export event main
function exportEvent(event_id){
    url = '/api/v2/events/' + event_id + '/export/json';
    $('#btnExportEvent').click();
    jQuery.ajax({
        url: url,
        type: 'GET',
        success: function(data){
            $('#export_status').text('Status: Queued');
            setTimeout(function(){
                exportTask(data['task_url']);
            }, 1000);
        },
        error: function(x){
            obj = JSON.parse(x.responseText);
            console.log(obj);
            $('#export_status').text('');
            $('#export_error').text(obj['message']);
        }
    });
}

// export event task
function exportTask(url){
    jQuery.ajax({
    url: url,
    type: 'GET',
    success: function(data){
        console.log(data);
        if (data['state'] != 'SUCCESS'){
            $('#export_status').text('Status: ' + data['state']);
            setTimeout(function(){
                exportTask(url);
            }, 3000);
        } else {
            $('#export_status').text('Status: ' + data['state']);
            $('#btnExportEvent').prop('disabled', false);
            $('#btnExportEvent').click(function(){
                document.location = data['result']['download_url'];
            });
        }
    },
    error: function(x){
        obj = JSON.parse(x.responseText);
        console.log(obj);
        $('#export_status').text('');
        $('#export_error').text(obj['message']);
    }
    });
}
