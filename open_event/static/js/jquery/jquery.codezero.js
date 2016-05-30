/**
 * Created by Niranjan on 29-May-16.
 */
jQuery.fn.extend({
    valueChange: function (callback) {
        return this.each(function () {
            var elem = $(this);
            elem.data('oldVal', elem.val());
            elem.bind("propertychange change click keyup input paste", function (event) {
                if (elem.data('oldVal') != elem.val()) {
                    elem.data('oldVal', elem.val());
                    callback(elem.val(), event);
                }
            });
        });
    }
});


var cache = _.memoize(function(pattern){
  return new RegExp(pattern.split("").reduce(function(a,b){
    return a+'[^'+b+']*'+b;
  }), 'i');
});

function fuzzy_match(str,pattern){
  return cache(pattern).test(str)
}

function roundOffToMultiple(val, multiple) {
    if (!multiple) {
        multiple = 6;
    }
    if (val > 0) {
        var roundUp = Math.ceil(val / multiple) * multiple;
        var roundDown = Math.floor(val / multiple) * multiple;

        if (val >= roundDown + 12) {
            return roundUp;
        } else {
            return roundDown;
        }

    } else {
        return multiple;
    }
}

/**
 * @return {boolean}
 */
function horizontallyBound($parentDiv, $childDiv, offsetAdd) {
    var pageWidth = $parentDiv.width();
    var pageHeight = $parentDiv.height();
    var pageTop = $parentDiv.offset().top;
    var pageLeft = $parentDiv.offset().left;
    var elementWidth = $childDiv.width();
    var elementHeight = $childDiv.height();
    var elementTop = $childDiv.offset().top;
    var elementLeft = $childDiv.offset().left;
    var offset = 50 + offsetAdd;
    return !!((elementLeft + offset >= pageLeft) && (elementTop + offset >= pageTop) && (elementLeft + elementWidth <= pageLeft + pageWidth) && (elementTop + elementHeight <= pageTop + pageHeight));
}

// Borrowed from http://stackoverflow.com/a/5541252/1562480. Author: BC.
function collision($div1, $div2) {
    var x1 = $div1.offset().left;
    var y1 = $div1.offset().top;
    var h1 = $div1.outerHeight(true);
    var w1 = $div1.outerWidth(true);
    var b1 = y1 + h1;
    var r1 = x1 + w1;
    var x2 = $div2.offset().left;
    var y2 = $div2.offset().top;
    var h2 = $div2.outerHeight(true);
    var w2 = $div2.outerWidth(true);
    var b2 = y2 + h2;
    var r2 = x2 + w2;
    return !(b1 < y2 || y1 > b2 || r1 < x2 || x1 > r2);
}


