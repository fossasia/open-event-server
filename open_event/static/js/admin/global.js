/**
 * Created by Niranjan on 14-Jun-16.
 */
var summernoteConfig = {
    toolbar: [
        ['style', ['bold', 'italic', 'underline', 'clear']],
        ['font', ['strikethrough', 'superscript', 'subscript']],
        ['para', ['ul', 'ol', 'paragraph']]
    ],
    height: 150,
    disableDragAndDrop: true
};

function imgError(image) {
    image.onerror = "";
    image.src = '/static/img/avatar.png';
    return true;
}
