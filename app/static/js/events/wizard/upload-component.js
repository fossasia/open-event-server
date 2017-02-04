function resetFormElement(e) {
    e = $(e);
    e.wrap('<form>').closest('form').get(0).reset();
    e.unwrap();
}

Vue.component('image-upload', {
    props: {
        title: {
            type: String,
            required: true
        },
        icon: {
            type: String,
            default: function () {
                return 'fa-file-image-o';
            }
        },
        helpText: {
            type: String,
            default: function () {
                return '';
            }
        },
        imageUrl: {
            type: String,
            default: function () {
                return '';
            }
        },
        uploadUrl: {
            type: String,
            default: function () {
                return '/events/create/files/image/';
            }
        },
        maxSizeInMb: {
            type: Number,
            required: true
        },
        cropRequired: {
            type: Boolean,
            default: function () {
                return false;
            }
        },
        cropperConfig: {
            type: Object,
            default: function () {
                return {
                    viewport: {
                        width: 490,
                        height: 245,
                        type: 'square'
                    },
                    boundary: {
                        width: 508,
                        height: 350
                    }
                };
            }
        },
        value: {
            type: String
        }
    },
    data: function () {
        return {
            isUploading: false,
            errorMessage: '',
            componentId: 'upload-component-' + _.random(1000, 9999)
        };
    },
    template: '#image-upload-template',
    methods: {
        uploadImage: function (e) {
            var input = e.target;
            var $this = this;
            $this.errorMessage = '';
            if (input.files && input.files[0]) {
                if (input.files[0].size > ($this.maxSizeInMb * 1024 * 1024)) {
                    createSnackbar("Image must be less than " + $this.maxSizeInMb + " MB in size");
                    resetFormElement(input);
                } else {
                    var reader = new FileReader();
                    reader.onload = function (e) {
                        var untouchedImageData = e.target.result;
                        if ($this.cropRequired) {
                            $this.$uploadCropperModal.unbind('shown.bs.modal').on('shown.bs.modal', function () {
                                $this.$uploadCropper.croppie('bind', {
                                    url: untouchedImageData
                                });
                            });
                            $this.$uploadCropperModal.modal("show");
                        } else {
                            $this.uploadImageToServer(untouchedImageData, function () {
                                $this.$emit('uploaded');
                            });
                        }
                    };
                    reader.readAsDataURL(input.files[0]);
                }
            }
            else {
                $this.errorMessage = "No FileReader support. Please use a more latest browser";
            }
        },
        saveCrop: function () {
            var $this = this;
            $this.$uploadCropper.croppie('result', {
                type: 'canvas',
                size: 'original'
            }).then(function (resp) {
                $this.$uploadCropperModal.modal('hide');
                $this.uploadImageToServer(resp, function () {
                    $this.$emit('uploaded');
                });
            });
        },
        deleteImage: function () {
            this.$emit('input', '');
        },
        uploadImageToServer: function (imageData, callback) {
            var $this = this;
            $this.isUploading = true;
            $this.$emit("uploading");
            $.ajax({
                type: 'POST',
                url: this.uploadUrl,
                data: {
                    image: imageData
                },
                dataType: 'json'
            }).done(function (data) {
                $this.$emit('input', String(data.image_url));
                callback();
            }).fail(function () {
                $this.errorMessage = "Something went wrong. Please try again.";
                $this.$emit("error");
            }).always(function () {
                $this.isUploading = false;
            });
        }
    },
    mounted: function () {
        this.$nextTick(function () {
            var $div = $(this.$el);
            if (this.cropRequired) {
                this.$uploadCropperModal = $div.find('.cropper-modal');
                this.$uploadCropper = $div.find('.upload-cropper');
                this.$uploadCropper.croppie(this.cropperConfig);
            }
        });
    }
});
