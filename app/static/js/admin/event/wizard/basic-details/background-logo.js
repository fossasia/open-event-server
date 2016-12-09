var $uploadCropper = $form.find('#upload-cropper');

$uploadCropper = $uploadCropper.croppie({
    viewport: {
        width: 490,
        height: 245,
        type: 'square'
    },
    boundary: {
        width: 508,
        height: 350
    }
});

$("#event-image-upload").unbind("change").on('change', function () {
    var input = this;
    if (input.files && input.files[0]) {
        if (input.files[0].size > 10485760) {
            createSnackbar("Image must be less than 10 MB in size");
            resetFormElement(input);
        } else {
            var reader = new FileReader();
            reader.onload = function (e) {
                $form.find("#cropper-modal").modal("show");
                $uploadCropper.croppie('bind', {
                    url: e.target.result
                });
            };
            reader.readAsDataURL(input.files[0]);
        }
    }
    else {
        logError("No FileReader support");
    }

});

$("#logo-upload").unbind("change").on('change', function () {
    var input = this;
    if (input.files && input.files[0]) {
        if (input.files[0].size > 1048576) {
            createSnackbar("Image must be less than 1 MB in size");
            resetFormElement(input);
        } else {
            var reader = new FileReader();
            reader.onload = function (e) {
                $("#logo-upload-label").html(loadingImage);
                $(".save-event").prop("disabled", true);
                $(".publish-unpublish-event").prop("disabled", true);
                $.ajax({
                    type: 'POST',
                    url: logoUploadUrl,
                    data: {logo: e.target.result},
                    dataType: 'json'
                }).done(function (data) {
                    console.log(data);
                    resetFormElement(input);
                    $("#logo").val(data.logo);
                    $("#logo-upload-group").hide();
                    $("#logo-view-group").show().find("img").attr("src", e.target.result);
                }).fail(function (data) {
                    alert("Something went wrong. Please try again.");
                }).always(function () {
                    $("#logo-upload-label").html('<i class="fa fa-4x fa-file-image-o" aria-hidden="true"></i> <br> <h3>Select Logo</h3>');
                    /* Enable Save Event buttons */
                    $(".save-event").prop("disabled", false);
                    $(".publish-unpublish-event").prop("disabled", false);
                });
            };
            reader.readAsDataURL(input.files[0]);
        }
    }
    else {
        logError("No FileReader support");
    }

});


$("#save-crop").click(function () {
    $uploadCropper.croppie('result', {
        type: 'canvas',
        size: 'original'
    }).then(function (resp) {
        $('#cropper-modal').modal('hide');
        $("#event-image-upload-label").html(loadingImage);
        $(".save-event").prop("disabled", true);
        $(".publish-unpublish-event").prop("disabled", true);
        $.ajax({
            type: 'POST',
            url: backgroundUploadUrl,
            data: {bgimage: resp},
            dataType: 'json'
        }).done(function (data) {
            console.log(data);
            $("#background_url").val(data.background_url);
            $("#image-view-group").show().find("img").attr("src", resp);
            $("#image-upload-group").hide();
        }).fail(function (data) {
            alert("Something went wrong. Please try again.");
        }).always(function () {
            $("#event-image-upload-label").html('<i class="fa fa-4x fa-camera-retro" aria-hidden="true"></i><br><h3>Select Event Image</h3>');
            /* Enable Save Event buttons */
            $(".save-event").prop("disabled", false);
            $(".publish-unpublish-event").prop("disabled", false);
        });
    });
});

if (isEdit) {
    $("#remove-image-btn").click(function () {
        $.ajax({
            type: 'DELETE',
            url: backgroundUploadUrl,
            dataType: 'json'
        }).done(function (data) {
            console.log(data);
            $("#image-view-group").hide();
            $("#image-upload-group").show();
            $("#background_url").val('');
        }).fail(function (data) {
            alert("Something went wrong. Please try again.");
        });
    });

    $("#remove-logo-btn").click(function () {
        $.ajax({
            type: 'DELETE',
            url: logoUploadUrl,
            dataType: 'json'
        }).done(function (data) {
            console.log(data);
            $("#logo-view-group").hide();
            $("#logo-upload-group").show();
            $("#logo").val('');
        }).fail(function (data) {
            alert("Something went wrong. Please try again.");
        });
    });


} else {
    $("#remove-image-btn").click(function () {
        $("#image-view-group").hide();
        $("#image-upload-group").show();
        $("#background_url").val('');
    });

    $("#remove-logo-btn").click(function () {
        $("#logo-view-group").hide();
        $("#logo-upload-group").show();
        $("#logo").val('');
    });
}


$('#cropper-modal').on('shown.bs.modal', function (e) {
    $uploadCropper.croppie('bind');
    resetFormElement($("#event-image-upload"));
});
