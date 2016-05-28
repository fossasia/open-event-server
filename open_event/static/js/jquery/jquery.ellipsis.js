// Borrowed from http://stackoverflow.com/a/1022672/1562480
(function ellipsisInit($) {
    $.fn.ellipsis = function () {
        return this.each(function () {
            var el = $(this);

            var text = el.attr("data-original-text");
            el.find(".text").text(text);

            var multiline = true;

            var t = $(this.cloneNode(true))
                    .hide()
                    .css("position", "absolute")
                    .css("overflow", "visible")
                    .width(multiline ? el.width() : "auto")
                    .height(multiline ? "auto" : el.height())
                ;

            el.after(t);

            function height() {
                return t.height() > el.height();
            }

            function width() {
                return t.width() > el.width();
            }

            var func = multiline ? height : width;


            while (text.length > 0 && func()) {
                text = text.substr(0, text.length - 1);
                t.text(text + "...");

            }

            el.find(".text").text(t.text());
            t.remove();
        });
    };
})(jQuery);
