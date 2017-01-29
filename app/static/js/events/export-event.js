// export event main
function exportEvent(event_id, current_user_email) {
    var url = '/api/v1/events/' + event_id + '/export/json';
    // generate payload
    var fields = ['image', 'video', 'audio', 'document'];
    var payload = {};
    for (var i = 0; i < 4; i++) {
        payload[fields[i]] = !!$('#exportForm').find('[name=' + fields[i] + ']').is(':checked');
    }
    $('#btnExportEvent').unbind('click').prop('disabled', true); // in case of second export
    $('#btnStartExport').prop('disabled', true);
    // set creator user
    $('#export_creator').show();
    $('#export_creator_email').text(current_user_email);
    $('#export_creator_datetime').text('now');

    jQuery.ajax({
        url: url,
        type: 'POST',
        data: JSON.stringify(payload),
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        cache: false,
        success: function (data) {
            $('#export_status').text('Status: Queued');
            setTimeout(function () {
                exportTask(data['task_url']);
            }, 1000);
        },
        error: function (x) {
            var obj = JSON.parse(x.responseText);
            $('#export_status').html('<span class="red">' + obj['message'] + '</span>');
        }
    });
}

// export event task
function exportTask(url) {
    jQuery.ajax({
        url: url,
        type: 'GET',
        success: function (data) {
            if (data['state'] != 'SUCCESS') {
                $('#export_status').text('Status: ' + data['state']);
                setTimeout(function () {
                    exportTask(url);
                }, 3000);
            } else {
                $('#export_status').text('Status: ' + data['state']);
                $('#btnStartExport').prop('disabled', false);
                $('#btnExportEvent').prop('disabled', false).click(function () {
                    document.location = data['result']['download_url'];
                });
            }
        },
        error: function (x) {
            var obj = JSON.parse(x.responseText);
            $('#export_status').html('<span class="red">' + obj['message'] + '</span>');
            $('#btnStartExport').prop('disabled', false);
        }
    });
}

// load previous job data
function loadPreviousJob(task_url, user_email, start_time) {
    $('#export_status').text('Loading...');
    if (task_url) {
        isTaskInvalid(task_url, user_email, start_time);
    } else {
        noPreviousJob();
    }
}

// no previous job
function noPreviousJob() {
    $('#btnStartExport').prop('disabled', false);
    $('#export_status').text('');
}

// load data about previous job helper (real) function
function loadPreviousJob_(task_url, user_email, start_time) {
    if (user_email) {
        $('#export_creator').show();
        $('#export_creator_email').text(user_email);
        $('#export_creator_datetime').text(start_time);
    }
    if (task_url) {
        exportTask(task_url);
    }
}

// is task old and not available on redis
function isTaskInvalid(task_url, user_email, start_time) {
    jQuery.ajax({
        url: task_url,
        type: 'GET',
        success: function (data) {
            if (data['state'] == 'PENDING') {
                noPreviousJob();
            } else {
                loadPreviousJob_(task_url, user_email, start_time);
            }
        },
        error: function (x) {
            noPreviousJob();
            loadPreviousJob_(task_url, user_email, start_time);
        }
    });
}
