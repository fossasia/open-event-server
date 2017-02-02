$(document).ready(function () {
    $('#add-speakers').click(function () {
        var row = '<div class="item form-group">' +
            '<label class="control-label">Email </label>' +
            '<div class="">' +
            '<input type="text" class="form-control col-md-7 col-sm-7" name="speakers[email]" placeholder="Email Address of Speaker" style="width:60%;">' +
            '</div>' +
            '<div class="col-sm-1 col-md-1 input-group">' +
            '<span class="input-group-btn">' +
            '<button type="button" class="btn btn-danger" id="remove-speakers">-</button>' +
            '</span>' +
            '</div>' +
            '</div>';
        $('.speakers').append(row);
    });

    $("body").on("click", "#remove-speakers", function () {
        $(this).parent().parent().parent().remove();
    });
});

var remove_url = function (name) {
    $('input[name="' + name + '_url"]').val("");
    $('#media-progress-' + name).hide();
};

var fileUpload = function(name, media){
    var fd = new FormData();
    fd.append(name, media.files[0]);
    filename = media.files[0].name;
    $('#download-' + name).text(filename);
    $('#media-progress-' + name).show();
    $('#progress-' + name).show();
    $.ajax({
        xhr: function(){
            var xhr = new window.XMLHttpRequest();
            //Upload progress
            xhr.upload.addEventListener("progress", function(evt){
              if (evt.lengthComputable) {
                 var percentComplete = (evt.loaded / evt.total) * 100;
                 $('#progress-bar-' + name).width(percentComplete + '%');
              }
            }, false);
            return xhr;
          },
        dataType: 'json',
        url: '/e/temp/',
        type: 'POST',
        data: fd,
        success: function(data){
            if(data.url){
                $('input[name="' + name + '_url"]').val(data.url);
                $('#download-' + name).attr("href", data.url);
                $('#progress-bar-' + name).removeClass('active');
            }
        },
        contentType: false,
        processData: false
    });
};

$('input[name="slides"]').on('change', function(){
    fileUpload('slides', this);
});
$('input[name="video"]').on('change', function(){
    fileUpload('video', this);
});
$('input[name="audio"]').on('change', function(){
    fileUpload('audio', this);
});
