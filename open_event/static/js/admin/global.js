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

function imgError(image, transparent) {
    image.onerror = "";
    if(transparent) {
        image.src = '/static/img/trans_white.png';
    } else {
        image.src = '/static/img/avatar.png';
    }
    return true;
}

function setSocialLinks(url, title) {
    var $socialLinks = $(".social-links").find("a");
    $.each($socialLinks, function (index, $link) {
        $link = $($link);
        var linkUrl = $link.attr("data-href");
        linkUrl = linkUrl.replace("{url}", url);
        linkUrl = linkUrl.replace("{title}", title);
        $link.attr("href", linkUrl);
    });
}
