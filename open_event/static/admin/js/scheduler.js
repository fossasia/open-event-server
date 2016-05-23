/**
 * Created by Niranjan on 23-May-16.
 */
(function ($) {
    $(document).ready(function () {
        /**
         *  24px == 15 minutes
         *  (Smallest unit of measurement is 15 minutes)
         *
         */

        // TIME SETTINGS
        var time = {
            start: {
                hours: 9,
                minutes: 0
            },
            end: {
                hours: 17,
                minutes: 0
            },
            unit: {
                minutes: 15,
                pixels: 24
            }
        };

        interact('.session')
            .draggable({
                // enable inertial throwing
                inertia: false,
                // enable autoScroll
                autoScroll: false,
                // call this function on every dragmove event
                onmove: function (event) {
                    var $sessionElement = $(event.target),
                        x = (parseFloat($sessionElement.data('x')) || 0) + event.dx,
                        y = (parseFloat($sessionElement.data('y')) || 0) + event.dy;

                    $sessionElement.css("-webkit-transform", 'translate(' + x + 'px, ' + y + 'px)');
                    $sessionElement.css("transform", 'translate(' + x + 'px, ' + y + 'px)');

                    $sessionElement.data('x', x);
                    $sessionElement.data('y', y);
                    $sessionElement.data("top", roundOffToMultiple($sessionElement.offset().top - $(".rooms.x1").offset().top));
                },
                // call this function on every dragend event
                onend: function (event) {

                }
            });


        interact('.session')
            .resizable({
                preserveAspectRatio: false,
                enabled: true,
                edges: {left: false, right: false, bottom: true, top: false}
            })
            .on('resizemove', function (event) {
                if ($(event.target).hasClass("scheduled")) {
                    var target = event.target,
                        x = (parseFloat(target.getAttribute('data-x')) || 0),
                        y = (parseFloat(target.getAttribute('data-y')) || 0);

                    // update the element's style
                    target.style.width = roundOffToMultiple(event.rect.width) + 'px';
                    target.style.height = roundOffToMultiple(event.rect.height) + 'px';

                    updateElementTime($(event.target));
                }
            });

        interact('.track-inner').dropzone({
            // only accept elements matching this CSS selector
            accept: '.session',
            // Require a 75% element overlap for a drop to be possible
            overlap: 0.50,

            ondropactivate: function (event) {
                $(event.target).addClass('drop-active');
            },
            ondragenter: function (event) {
                $(event.target).addClass('drop-now');
            },
            ondragleave: function (event) {
                $(event.target).removeClass('drop-now');
            },
            ondrop: function (event) {
                var $sessionElement = $(event.relatedTarget);
                var $trackDropZone = $(event.target);
                $sessionElement.removeClass('unscheduled').addClass('scheduled');
                $trackDropZone.removeClass('drop-active').removeClass('drop-now');

                $sessionElement.css({
                    "-webkit-transform": "",
                    "transform": ""
                }).removeData("x").removeData("y");

                $sessionElement.appendTo($trackDropZone);
                $sessionElement.css("top", $sessionElement.data("top") + "px");

                var isColliding = sessionOverlapTest($trackDropZone, $sessionElement);
                if (!isColliding) {
                    updateCounterBadge();
                    updateElementTime($sessionElement);
                    updateColor($sessionElement);
                } else {
                    $sessionElement.appendTo($(".sessions-holder"));
                    $sessionElement.addClass('unscheduled').removeClass('scheduled');
                }

            },
            ondropdeactivate: function (event) {
                var $trackDropZone = $(event.target);
                var $sessionElement = $(event.relatedTarget);
                $trackDropZone.removeClass('drop-now').removeClass('drop-active');
                if (!$sessionElement.hasClass("scheduled")) {
                    $sessionElement.css({
                        "-webkit-transform": "",
                        "transform": ""
                    }).removeData("x").removeData("y");
                }
            }
        });


        var $tracks = $(".track");

        function updateCounterBadge() {
            $.each($tracks, function (index, $track) {
                $track = $($track);
                var sessionsCount = $track.find(".track-inner > .session.scheduled").length;
                $track.find(".track-header > .badge").text(sessionsCount);
            });
        }

        function roundOffToMultiple(val, multiple) {
            if (!multiple) {
                multiple = 24;
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

        function sessionOverlapTest($track, $session) {
            var $otherSessions = $track.find(".session.scheduled");
            var returnVal;
            returnVal = false;
            $.each($otherSessions, function (index, $otherSession) {
                $otherSession = $($otherSession);
                if (!$otherSession.is($session) && collision($otherSession, $session)) {
                    returnVal = $otherSession;
                }
            });
            return returnVal;
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

        function updateColor($element) {
            $element.css("background-color", randomColor({
                hue: 'green',
                luminosity: 'dark'
            }));
        }

        /*
         *
         *
         */

        // TODO Store data into this object
        var timeline = {
            days: ["May 18", "May 19", "May 20"],
            tracks: [
                {
                    name: "Android Track",
                    sessions: [
                        {
                            id: 1,
                            top: 23,
                            mins: 33,
                            start: "09:00 AM",
                            end: "10:00 AM",
                            name: "Session 1"
                        }
                    ]
                }
            ]
        };

        function updateElementTime($element) {
            var startTime = moment({hour: time.start.hours, minute: time.start.minutes});
            var mins = ($element.outerHeight(false) / time.unit.pixels) * time.unit.minutes;
            var topInterval = (($element.data("top") - time.unit.pixels) / time.unit.pixels) * time.unit.minutes;

            var startTimeString = startTime.add(topInterval, 'm').format("LT");
            var endTimeString = startTime.add(topInterval + mins, "m").format("LT");

            $element.data("start-time", startTimeString).data("end-time", endTimeString);
            $element.find(".time").text(startTimeString + " to " + endTimeString);
        }

        function persistTimeline() {
            // TODO Create javascript object and persist to backed using AJAX
        }

    });
})(jQuery);
