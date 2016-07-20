// export event main
var event_id = 0;

function exportEvent(){
    url = '/api/v2/events/' + event_id + '/export/json';
    // generate payload
    fields = ['image', 'video', 'audio', 'document'];
    payload = {};
    for (i=0; i<4; i++){
        payload[fields[i]] = $('#exportForm [name=' + fields[i] + ']').is(':checked') ? true : false;
    }
    $('#btnExportEvent').unbind('click');

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


$('#exportModal').on('show.bs.modal', function(event){
    var button = $(event.relatedTarget);
    event_id = button.data('event-id');
    console.log(event_id);
});
