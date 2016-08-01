// export event main
function exportEvent(event_id){
    url = '/api/v2/events/' + event_id + '/export/json';
    // generate payload
    fields = ['image', 'video', 'audio', 'document'];
    payload = {};
    for (i=0; i<4; i++){
        payload[fields[i]] = $('#exportForm [name=' + fields[i] + ']').is(':checked') ? true : false;
    }
    $('#btnExportEvent').unbind('click');
    $('#btnExportEvent').prop('disabled', true); // in case of second export
    $('#btnStartExport').prop('disabled', true);

    jQuery.ajax({
        url: url,
        type: 'POST',
        data: JSON.stringify(payload),
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        cache: false,
        success: function(data){
            $('#export_status').text('Status: Queued');
            setTimeout(function(){
                exportTask(data['task_url']);
            }, 1000);
        },
        error: function(x){
            obj = JSON.parse(x.responseText);
            console.log(obj);
            $('#export_status').html('<span class="red">' + obj['message'] + '</span>');
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
            $('#btnStartExport').prop('disabled', false);
            $('#btnExportEvent').click(function(){
                document.location = data['result']['download_url'];
            });
        }
    },
    error: function(x){
        obj = JSON.parse(x.responseText);
        console.log(obj);
        $('#export_status').html('<span class="red">' + obj['message'] + '</span>');
        $('#btnStartExport').prop('disabled', false);
    }
    });
}
