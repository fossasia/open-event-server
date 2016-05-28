/**
 * Created by Niranjan on 23-May-16.
 */
/**
 *  24px == 15 minutes
 *  (Smallest unit of measurement is 15 minutes)
 *
 */

// TIME SETTINGS
var time = {
    start: {
        hours: 0,
        minutes: 0
    },
    end: {
        hours: 23,
        minutes: 59
    },
    unit: {
        minutes: 15,
        pixels: 24,
        count: 0
    }
};

/*
 *
 *
 */

var $tracks = $(".track");

function updateCounterBadge() {
    $tracks = $(".track");
    $.each($tracks, function (index, $track) {
        $track = $($track);
        var sessionsCount = $track.find(".session.scheduled").length;
        $track.find(".track-header > .badge").text(sessionsCount);
    });
}


function fixOverlaps() {
    $tracks = $(".track");
    $.each($tracks, function (index, $track) {
        $track = $($track);
        var $sessionElements = $track.find(".session.scheduled");
        $.each($sessionElements, function (index, $sessionElement) {
            $sessionElement = $($sessionElement);
            var isColliding = sessionOverlapTest($track, $sessionElement);
            if (!isColliding) {

            } else {
                $sessionElement.appendTo($(".sessions-list"));
                $sessionElement.addClass('unscheduled').removeClass('scheduled').tooltip("hide").attr("data-original-title", "");
                $sessionElement.css({
                    "-webkit-transform": "",
                    "transform": "",
                    "background-color": ""
                }).removeData("x").removeData("y");
                $(".no-sessions-info").hide();
            }
        });
    });
    updateCounterBadge();
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

function restrictionCheck(x, $sessionElement) {
    return (horizontallyBound($(".tracks"), $sessionElement, 0));
}

function overDraggable($sessionElement) {
    return collision($(".tracks"), $sessionElement);
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
    $element.css("background-color", palette.random("800"));
    $element.css("background-color", palette.random("800"));
}

function updateElementTime($element) {
    var topTime = moment.utc({hour: time.start.hours, minute: time.start.minutes});
    var mins = pixelsToMinutes($element.outerHeight(false));
    var topInterval = pixelsToMinutes($element.data("top"), true);

    var startTimeString = topTime.add(topInterval, 'm').format("LT");
    var endTimeString = topTime.add(mins, "m").format("LT");

    $element.data("start-time", startTimeString).data("end-time", endTimeString);
    $element.attr("data-original-title", startTimeString + " to " + endTimeString);
    $element.tooltip("show");
}

function initializeInteractables() {

    $tracks = $(".track");

    interact(".session")
        .draggable({
            // enable inertial throwing
            inertia: false,
            // enable autoScroll
            autoScroll: {
                container: $(".track-container")[0],
                margin: 50,
                distance: 5,
                interval: 10
            },
            restrict: {
                restriction: ".draggable-holder"
            },
            // call this function on every dragmove event
            onmove: function (event) {
                var $sessionElement = $(event.target),
                    x = (parseFloat($sessionElement.data('x')) || 0) + event.dx,
                    y = (parseFloat($sessionElement.data('y')) || 0) + event.dy;

                if (restrictionCheck(x, $sessionElement) || $sessionElement.hasClass("unscheduled")) {
                    $sessionElement.css("-webkit-transform", "translate(" + x + "px, " + y + "px)");
                    $sessionElement.css("transform", "translate(" + x + "px, " + y + "px)");

                    $sessionElement.data('x', x);
                    $sessionElement.data('y', y);
                }

                if (overDraggable($sessionElement)) {
                    updateElementTime($sessionElement);
                } else {
                    $sessionElement.tooltip("hide").attr("data-original-title", "");
                }

                $sessionElement.data("top", roundOffToMultiple($sessionElement.offset().top - $(".tracks.x1").offset().top));
            },
            // call this function on every dragend event
            onend: function (event) {

            }
        });


    interact(".session")
        .resizable({
            preserveAspectRatio: false,
            enabled: true,
            edges: {left: false, right: false, bottom: true, top: false}
        })
        .on("resizemove", function (event) {
            if ($(event.target).hasClass("scheduled")) {
                var target = event.target,
                    x = (parseFloat(target.getAttribute("data-x")) || 0),
                    y = (parseFloat(target.getAttribute("data-y")) || 0);

                // update the element's style
                target.style.width = roundOffToMultiple(event.rect.width) + "px";
                target.style.height = roundOffToMultiple(event.rect.height) + "px";

                $(event.target).ellipsis();

                updateElementTime($(event.target));
            }
        });

    interact(".track-inner").dropzone({
        // only accept elements matching this CSS selector
        accept: ".session",
        // Require a 75% element overlap for a drop to be possible
        overlap: 0.50,

        ondropactivate: function (event) {
            $(event.target).addClass("drop-active");
        },
        ondragenter: function (event) {
            $(event.target).addClass("drop-now");
        },
        ondragleave: function (event) {
            $(event.target).removeClass("drop-now");
        },
        ondrop: function (event) {
            var $sessionElement = $(event.relatedTarget);
            var $trackDropZone = $(event.target);
            $sessionElement.removeClass("unscheduled").addClass("scheduled");
            $trackDropZone.removeClass("drop-active").removeClass("drop-now");

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
                $sessionElement.addClass("unscheduled").removeClass("scheduled").tooltip("hide").attr("data-original-title", "");
                $sessionElement.css({
                    "-webkit-transform": "",
                    "transform": "",
                    "background-color": ""
                }).removeData("x").removeData("y");
            }

        },
        ondropdeactivate: function (event) {
            var $trackDropZone = $(event.target);
            var $sessionElement = $(event.relatedTarget);
            $trackDropZone.removeClass("drop-now").removeClass("drop-active");
            if (!$sessionElement.hasClass("scheduled")) {
                $sessionElement.css({
                    "-webkit-transform": "",
                    "transform": "",
                    "background-color": ""
                }).removeData("x").removeData("y").tooltip("hide").attr("data-original-title", "");
            }
        }
    });
}

function minutesToPixels(minutes, forTop) {
    minutes = Math.abs(minutes);
    if (forTop) {
        return ((minutes / time.unit.minutes) * time.unit.pixels) + time.unit.pixels;
    } else {
        return (minutes / time.unit.minutes) * time.unit.pixels;
    }
}

function pixelsToMinutes(pixels, fromTop) {
    pixels = Math.abs(pixels);
    if (fromTop) {
        return ((pixels - time.unit.pixels) / time.unit.pixels) * time.unit.minutes;
    } else {
        return (pixels / time.unit.pixels) * time.unit.minutes;
    }
}

var days = [];
var sessionsStore = [];
var tracksStore = [];

function processTrackSession(tracks, sessions, callback) {

    var topTime = moment.utc({hour: time.start.hours, minute: time.start.minutes});

    _.each(sessions, function (session) {

        var startTime = moment.utc(session.start_time);
        var endTime = moment.utc(session.end_time);
        var duration = moment.duration(endTime.diff(startTime));

        var top = minutesToPixels(moment.duration(moment.utc({
            hour: startTime.hours(),
            minute: startTime.minutes()
        }).diff(topTime)).asMinutes(), true);

        console.log(session.start_time);

        var dayString = startTime.format("Do MMMM YYYY"); // formatted as eg. 2nd May

        if (!_.contains(days, dayString)) {
            days.push(dayString);
        }

        var sessionObject = {
            id: session.id,
            title: session.title,
            top: top,
            duration: Math.abs(duration.asMinutes()),
            track_id: session.track.id,
            start_time: startTime.format("HH:mm"),
            end_time: endTime.format("HH:mm")
        };

        var dayIndex = _.indexOf(days, dayString);

        if (_.isArray(sessionsStore[dayIndex])) {
            sessionsStore[dayIndex].push(sessionObject);
        } else {
            sessionsStore[dayIndex] = [sessionObject]
        }

    });

    _.each(tracks, function (track) {
        var tracksObject = {
            name: track.name,
            id: track.id,
            count: track.sessions.length
        };
        if (!_.contains(tracksStore, tracksObject)) {
            tracksStore.push(tracksObject);
        }
    });


    loadDateButtons();
    callback();
}

function loadDateButtons() {
    var dayButtonTemplate = $("#date-change-button-template").html();
    var $dayButtonsHolder = $(".date-change-btn-holder");
    var sortedDays = days.sort();
    _.each(sortedDays, function (day, index) {
        var $dayButton = $(dayButtonTemplate);
        if (index == 0) {
            $dayButton.addClass("active");
        }
        $dayButton.text(day);
        $dayButtonsHolder.append($dayButton)
    });
    loadTracksToTimeline(sortedDays[0]);
}

function loadTracksToTimeline(day) {

    var dayIndex = _.indexOf(days, day);
    var trackTemplate = $("#track-template").html();
    var sessionTemplate = $("#session-template").html();

    var $tracksHolder = $(".track-container");
    var $unscheduledSessionsHolder = $(".sessions-list");

    $tracksHolder.html("");
    $unscheduledSessionsHolder.html("");

    var $trackElement = $(trackTemplate);
    $trackElement.data("track-id", 0);
    $trackElement.find(".track-header").html("Standalone &nbsp;&nbsp;&nbsp;<span class='badge'>0</span>");
    $trackElement.find(".track-inner").css("height", time.unit.count * time.unit.pixels + "px");
    $tracksHolder.append($trackElement);

    _.each(tracksStore, function (track) {
        var $trackElement = $(trackTemplate);
        $trackElement.attr("data-track-id", track.id);
        $trackElement.find(".track-header").html(track.name + "&nbsp;&nbsp;&nbsp;<span class='badge'>0</span>");
        $trackElement.find(".track-inner").css("height", time.unit.count * time.unit.pixels + "px");
        $tracksHolder.append($trackElement);
    });

    _.each(sessionsStore[dayIndex], function (session) {
        var $sessionElement = $(sessionTemplate);
        $sessionElement.data("session-id", session.id);
        $sessionElement.attr("data-original-text", session.title);

        var scheduled = false;
        if (!_.isNull(session.start_time) && !_.isNull(session.end_time) && session.start_time != session.end_time) {
            scheduled = true;
        }

        if (scheduled) {
            $sessionElement.addClass("scheduled");
            $sessionElement.attr("data-original-title", session.start_time + " to " + session.end_time);
            updateColor($sessionElement);

            if (_.isNull(session.track_id)) {
                session.track_id = 0;
            }

            $sessionElement.data("top", session.top);
            $sessionElement.css("top", session.top + "px");
            $sessionElement.css("height", minutesToPixels(session.duration) + "px");
            $tracksHolder.find(".track[data-track-id=" + session.track_id + "]").append($sessionElement);
        } else {
            $sessionElement.addClass("unscheduled");
            $unscheduledSessionsHolder.append($sessionElement);
            $(".no-sessions-info").hide();
        }

        $sessionElement.ellipsis().ellipsis();

    });
    fixOverlaps();
    $("[data-toggle=tooltip]").tooltip();
}

function loadData(eventId, callback) {
    $.get("https://open-event.herokuapp.com/api/v2/events/" + eventId + "/tracks", function (tracks) {
        $.get("https://open-event.herokuapp.com/api/v2/events/" + eventId + "/sessions", function (sessions) {
            processTrackSession(tracks, sessions, callback);
        });
    });
}

$(document).on("click", ".date-change-btn", function () {
    $(this).addClass("active");
    loadTracksToTimeline($(this).text());
    $(this).siblings().removeClass("active");
});

$(document).on("click", ".session.scheduled > .remove-btn", function () {
    var $sessionElement = $(this).parent();
    $sessionElement.appendTo($(".sessions-holder"));
    $sessionElement.addClass("unscheduled").removeClass("scheduled").tooltip("hide").attr("data-original-title", "");
    $sessionElement.css({
        "-webkit-transform": "",
        "transform": "",
        "background-color": ""
    }).removeData("x").removeData("y");
});

function generateTimeUnits() {
    var start = moment.utc().hour(time.start.hours).minute(time.start.minutes).second(0);
    var end = moment.utc().hour(time.end.hours).minute(time.end.minutes).second(0);
    var $timeUnitsHolder = $(".timeunits");
    var timeUnitsCount = 1;
    while (start <= end) {
        var timeUnitDiv = $("<div class='timeunit'>" + start.format('HH:mm') + "</div>");
        $timeUnitsHolder.append(timeUnitDiv);
        start.add(time.unit.minutes, 'minutes');
        timeUnitsCount++;
    }
    $(".track-container").css("height", timeUnitsCount * time.unit.pixels);

    time.unit.count = timeUnitsCount;
}

$(document).ready(function () {

    generateTimeUnits();

    // TODO Load the event ID dynamically based on current event
    loadData(18, function () {
        $(".flash-message-holder").hide();
        $(".scheduler-holder").show();
        initializeInteractables();

    });

    $(".clear-overlaps-button").click(function () {
        fixOverlaps();
    });

    $(".timeline").scroll(function () {
        var cont = $(this);
        var el = $(cont.find(".track-inner")[0]);
        var elementTop = el.position().top;
        var pos = cont.scrollTop() + elementTop;
        console.log("scroll: "+ pos);
        cont.find(".track-header").css("top", pos + "px");
    });
});
