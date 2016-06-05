/**
 * Created by Niranjan on 23-May-16.
 */

/**
 *  TIME CONFIGURATION & MANIPULATION
 *  =================================
 *
 *  24px == 15 minutes
 *  (Smallest unit of measurement is 15 minutes)
 *
 */
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

/**
 * Convert minutes to pixels based on the time unit configuration
 * @param {number} minutes The minutes that need to be converted to pixels
 * @param {boolean} [forTop=false] Indicate whether top header compensation needs to be done
 * @returns {number} The pixels
 */
function minutesToPixels(minutes, forTop) {
    minutes = Math.abs(minutes);
    if (forTop) {
        return ((minutes / time.unit.minutes) * time.unit.pixels) + time.unit.pixels;
    } else {
        return (minutes / time.unit.minutes) * time.unit.pixels;
    }
}

/**
 * Convert pixels to minutes based on the time unit configuration
 * @param {number} pixels The pixels that need to be converted to minutes
 * @param {boolean} [fromTop=false] Indicate whether top header compensation needs to be done
 * @returns {number} The minutes
 */
function pixelsToMinutes(pixels, fromTop) {
    pixels = Math.abs(pixels);
    if (fromTop) {
        return ((pixels - time.unit.pixels) / time.unit.pixels) * time.unit.minutes;
    } else {
        return (pixels / time.unit.pixels) * time.unit.minutes;
    }
}

/**
 * IN-MEMORY DATA STORES
 * =====================
 *
 * @type {Array}
 */
var days = [];
var sessionsStore = [];
var tracksStore = [];
var unscheduledStore = [];

/**
 * jQuery OBJECT REFERENCES
 * ========================
 *
 * @type {jQuery|HTMLElement}
 */
var $timeline = $("#timeline");
var $tracks = $(".track");
var $unscheduledSessionsList = $("#sessions-list");
var $tracksHolder = $("#track-container");
var $unscheduledSessionsHolder = $unscheduledSessionsList;
var $noSessionsInfoBox = $("#no-sessions-info");
var $dayButtonsHolder = $("#date-change-btn-holder");

/**
 * TEMPLATE STRINGS
 * ================
 *
 * @type {string}
 */
var trackTemplate = $("#track-template").html();
var sessionTemplate = $("#session-template").html();
var dayButtonTemplate = $("#date-change-button-template").html();


/**
 * Data Getters
 * ============
 *
 */

/**
 *
 * @param {int|Object|jQuery} sessionRef Can be session ID, or session object or an existing session element from the target
 * @param {jQuery} $searchTarget the target to search for the element
 * @returns {Object} Returns object with session element and session object
 */
function getSessionFromReference(sessionRef, $searchTarget) {
    var $sessionElement;
    var session;
    var newElement = false;
    if (sessionRef instanceof jQuery) {
        $sessionElement = sessionRef;
        session = $sessionElement.data("session");
    } else if (_.isObjectLike(sessionRef)) {
        $sessionElement = $searchTarget.find(".session[data-session-id=" + sessionRef.id + "]");
        // If it's a new session, create session element from template and initialize
        if ($sessionElement.length == 0) {
            $sessionElement = $(sessionTemplate);
            $sessionElement.attr("data-session-id", sessionRef.id);
            $sessionElement.attr("data-original-text", sessionRef.title);
            $sessionElement.data("session", sessionRef);
            newElement = true;
            session = sessionRef;
        }
        session = sessionRef;
    } else if (_.isNumber(sessionRef)) {
        $sessionElement = $searchTarget.find(".session[data-session-id=" + sessionRef + "]");
        session = $sessionElement.data("session");
    } else {
        return false;
    }

    return {
        $sessionElement: $sessionElement,
        session: session,
        newElement: newElement
    }

}

/**
 * UI MANIPULATION METHODS
 * =======================
 *
 */

/**
 * Add a session to the timeline at the said position
 * @param {int|Object|jQuery} sessionRef Can be session ID, or session object or an existing session element from the unscheduled list
 * @param {Object} [position] Contains position information if the session is changed (track-id and top)
 * @param {boolean} [shouldBroadcast=true]
 */
function addSessionToTimeline(sessionRef, position, shouldBroadcast) {
    var sessionRefObject;
    if (_.isUndefined(position)) {
        sessionRefObject = getSessionFromReference(sessionRef, $unscheduledSessionsHolder);
    } else {
        sessionRefObject = getSessionFromReference(sessionRef, $tracksHolder);
    }

    if (!sessionRefObject) {
        logError("addSessionToTimeline", sessionRef);
        return false;
    }

    if (_.isNull(sessionRefObject.session.track_id)) {
        addSessionToUnscheduled(sessionRefObject.$sessionElement);
        return;
    }

    var oldTrack = sessionRefObject.session.track_id;
    var newTrack = null;

    if (!isUndefinedOrNull(position)) {
        sessionRefObject.session.top = position.top;
        sessionRefObject.session.track_id = position.track_id;
        newTrack = position.track_id;
        sessionRefObject.session = updateSessionTime(sessionRefObject.$sessionElement);
        sessionRefObject.$sessionElement.data("session", sessionRefObject.session);
    }

    sessionRefObject.$sessionElement.css({
        "-webkit-transform": "",
        "transform": ""
    }).removeData("x").removeData("y");

    sessionRefObject.$sessionElement.removeClass("unscheduled").addClass("scheduled");


    delete  sessionRefObject.session.start_time.isReset;
    delete  sessionRefObject.session.end_time.isReset;

    sessionRefObject.$sessionElement.css("top", sessionRefObject.session.top + "px");
    sessionRefObject.$sessionElement.css("height", minutesToPixels(sessionRefObject.session.duration) + "px");
    $tracksHolder.find(".track[data-track-id=" + sessionRefObject.session.track_id + "] > .track-inner").append(sessionRefObject.$sessionElement);

    sessionRefObject.$sessionElement.ellipsis().ellipsis();

    updateSessionTimeOnTooltip(sessionRefObject.$sessionElement);
    updateColor(sessionRefObject.$sessionElement);

    if (isUndefinedOrNull(shouldBroadcast) || shouldBroadcast) {
        if (!sessionRefObject.newElement) {
            $(document).trigger("scheduling:change", sessionRefObject.session);
        }

        $(document).trigger("scheduling:recount", [oldTrack, newTrack]);
    }

    _.remove(unscheduledStore, function (sessionTemp) {
        return sessionTemp.id == sessionRefObject.session.id
    });

}

/**
 * Remove a session from the timeline and add it to the Unscheduled list or create a session element and add to Unscheduled list
 * @param {int|Object|jQuery} sessionRef Can be session ID, or session object or an existing session element from the timeline
 * @param {boolean} [isFiltering=false]
 * @param {boolean} [shouldBroadcast=true]
 */
function addSessionToUnscheduled(sessionRef, isFiltering, shouldBroadcast) {
    var session;

    var sessionRefObject = getSessionFromReference(sessionRef, $tracksHolder);
    if (!sessionRefObject) {
        logError("addSessionToUnscheduled", sessionRef);
        return false;
    }

    var oldTrack = sessionRefObject.session.track_id;

    sessionRefObject.session.top = null;
    sessionRefObject.session.duration = 30;
    sessionRefObject.session.start_time.hours(0).minutes(0);
    sessionRefObject.session.end_time.hours(0).minutes(0);
    sessionRefObject.session.track_id = null;

    sessionRefObject.session.start_time.isReset = true;
    sessionRefObject.session.end_time.isReset = true;

    sessionRefObject.$sessionElement.data("session", session);
    $unscheduledSessionsHolder.append(sessionRefObject.$sessionElement);

    sessionRefObject.$sessionElement.addClass('unscheduled').removeClass('scheduled').tooltip("hide").attr("data-original-title", "");
    sessionRefObject.$sessionElement.css({
        "-webkit-transform": "",
        "transform": "",
        "background-color": "",
        "height": "48px",
        "top": ""
    }).removeData("x").removeData("y");

    sessionRefObject.$sessionElement.ellipsis().ellipsis();
    $noSessionsInfoBox.hide();

    if (isUndefinedOrNull(isFiltering) || !isFiltering) {
        if (isUndefinedOrNull(shouldBroadcast) || shouldBroadcast) {
            if (!sessionRefObject.newElement) {
                $(document).trigger("scheduling:change", sessionRefObject.session);
            }
            $(document).trigger("scheduling:recount", [oldTrack]);
        }
        unscheduledStore.push(sessionRefObject.session);
    }
}

/**
 * Update the counter badge that displays the number of sessions under each track
 * @param {array} trackIds An array of track IDs to recount
 */
function updateTrackSessionsCounterBadges(trackIds) {
    _.each(trackIds, function (trackId) {
        var $track = $tracksHolder.find(".track[data-track-id=" + trackId + "] > .track-inner");
        var sessionsCount = $track.find(".session.scheduled").length;
        $track.find(".track-header > .badge").text(sessionsCount);
    });
}

/**
 * Randomly generate and set a background color for an element
 * @param {jQuery} $element the element to be colored
 */
function updateColor($element) {
    $element.css("background-color", palette.random("800"));
    $element.css("background-color", palette.random("800"));
}

/**
 * Move any overlapping session to the unscheduled list. To be run as soon as timeline is initialized.
 */
function removeOverlaps() {
    var $sessionElements = $tracksHolder.find(".session.scheduled");
    _.each($sessionElements, function ($sessionElement) {
        $sessionElement = $($sessionElement);
        var isColliding = isSessionOverlapping($sessionElement);
        if (isColliding) {
            addSessionToUnscheduled($sessionElement);
        }
    });
}

/**
 * Check if a session is overlapping any other session
 * @param {jQuery} $session The session
 * @param {jQuery} [$track] The track to search in
 * @returns {boolean|jQuery} If no overlap, return false. If overlaps, return the session that's beneath.
 */
function isSessionOverlapping($session, $track) {
    if (isUndefinedOrNull($track)) {
        $track = $session.parent();
    }
    var $otherSessions = $track.find(".session.scheduled");
    var returnVal = false;
    _.each($otherSessions, function ($otherSession) {
        $otherSession = $($otherSession);
        if (!$otherSession.is($session) && collision($otherSession, $session)) {
            returnVal = $otherSession;
        }
    });
    return returnVal;
}

/**
 * Check if the session is within the timeline
 * @param {jQuery} $sessionElement the session element to check
 * @returns {boolean} Return true, if outside the boundary. Else, false.
 */
function isSessionRestricted($sessionElement) {
    return !horizontallyBound($tracks, $sessionElement, 0);
}

/**
 * Check if the session element is over the timeline
 * @param {jQuery} $sessionElement the session element to check
 * @returns {boolean}
 */
function isSessionOverTimeline($sessionElement) {
    return collision($tracks, $sessionElement);
}

/**
 * Update the session's time on it's tooltip and display it.
 * @param {jQuery} $sessionElement the target session element
 */
function updateSessionTimeOnTooltip($sessionElement) {
    var topTime = moment.utc({hour: time.start.hours, minute: time.start.minutes});
    var mins = pixelsToMinutes($sessionElement.outerHeight(false));
    var topInterval = pixelsToMinutes($sessionElement.data("temp-top"), true);

    var startTimeString = topTime.add(topInterval, 'm').format("LT");
    var endTimeString = topTime.add(mins, "m").format("LT");

    $sessionElement.attr("data-original-title", startTimeString + " to " + endTimeString);
    $sessionElement.tooltip("show");
}

/**
 * Update the session time and store to the session object
 * @param {jQuery} $sessionElement The session element to update
 * @param {object} [session] the session object to work on
 * @returns {*}
 */
function updateSessionTime($sessionElement, session) {

    var saveSession = false;
    if (_.isUndefined(session)) {
        session = $sessionElement.data("session");
        saveSession = true;
    }
    var topTime = moment.utc({hour: time.start.hours, minute: time.start.minutes});
    var duration = pixelsToMinutes($sessionElement.outerHeight(false));
    var topInterval = pixelsToMinutes($sessionElement.data("temp-top"), true);

    var newStartTime = topTime.add(topInterval, 'm');
    var newEndTime = topTime.add(duration, "m");

    session.duration = duration;
    session.start_time.hours(newStartTime.hours());
    session.start_time.minutes(newStartTime.minutes());

    session.end_time.hours(newEndTime.hours());
    session.end_time.minutes(newEndTime.minutes());

    if (saveSession) {
        $sessionElement.data("session", session);
    }

    return session;
}

/**
 * Add a new track to the timeline
 * @param {object} track The track object containing the details of the track
 */
function addTrackToTimeline(track) {
    var $trackElement = $(trackTemplate);
    $trackElement.attr("data-track-id", track.id);
    $trackElement.find(".track-header").html(track.name + "&nbsp;&nbsp;&nbsp;<span class='badge'>0</span>");
    $trackElement.find(".track-inner").css("height", time.unit.count * time.unit.pixels + "px");
    $tracksHolder.append($trackElement);
}

/**
 * Generate timeunits for the timeline
 */
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
    $tracksHolder.css("height", timeUnitsCount * time.unit.pixels);
    time.unit.count = timeUnitsCount;
}

/**
 *
 *
 *
 *
 *
 *
 *
 *
 *
 *
 *
 *
 *
 *
 *
 *
 *
 *
 */


/**
 * Initialize all the interactables necessary (drag-drop and resize)
 */
function initializeInteractables() {

    $tracks = $tracksHolder.find(".track");

    interact(".session")
        .draggable({
            // enable inertial throwing
            inertia: false,
            // enable autoScroll
            autoScroll: {
                container: $tracksHolder[0],
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

                $sessionElement.css("-webkit-transform", "translate(" + x + "px, " + y + "px)");
                $sessionElement.css("transform", "translate(" + x + "px, " + y + "px)");

                $sessionElement.data('x', x);
                $sessionElement.data('y', y);

                $sessionElement.data("temp-top", roundOffToMultiple($sessionElement.offset().top - $(".tracks.x1").offset().top));

                if (isSessionOverTimeline($sessionElement)) {
                    updateSessionTimeOnTooltip($sessionElement);
                } else {
                    $sessionElement.tooltip("hide").attr("data-original-title", "");
                }

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

                target.style.width = roundOffToMultiple(event.rect.width) + "px";
                target.style.height = roundOffToMultiple(event.rect.height) + "px";

                $(event.target).ellipsis();

                updateSessionTimeOnTooltip($(event.target));
            }
        })
        .on("resizeend", function (event) {
            if ($(event.target).hasClass("scheduled")) {
                var $sessionElement = $(event.target);
                updateSessionTime($sessionElement);
                $(document).trigger("scheduling:change", $sessionElement.data("session"));
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

            $trackDropZone.removeClass("drop-active").removeClass("drop-now");

            addSessionToTimeline($sessionElement, {
                track_id: parseInt($trackDropZone.parent().attr("data-track-id")),
                top: $sessionElement.data("temp-top")
            });

            var isColliding = isSessionOverlapping($sessionElement, $trackDropZone);
            if (!isColliding) {
                updateSessionTime($sessionElement);
            } else {
                createSnackbar("Session cannot be dropped onto another sessions.", "Try Again");
                addSessionToUnscheduled($sessionElement);
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

/**
 * This callback called after sessions and tracks are processed.
 * @callback postProcessCallback
 */
/**
 * Process the tracks and sessions data loaded from the server into in-memory data stores
 * @param {object} tracks The tracks json object
 * @param {object} sessions The sessions json object
 * @param {postProcessCallback} callback The post-process callback
 */
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

        var dayString = startTime.format("Do MMMM YYYY"); // formatted as eg. 2nd May 2013

        if (!_.includes(days, dayString)) {
            days.push(dayString);
        }

        /**
         * @type {{id: number, title: string, top: number, duration: number, track_id: number|null, start_time: Moment, end_time: Moment}}
         */
        var sessionObject = {
            id: session.id,
            title: session.title,
            top: top,
            duration: Math.abs(duration.asMinutes()),
            track_id: session.track.id,
            start_time: startTime,
            end_time: endTime
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
            id: track.id
        };
        if (!_.includes(tracksStore, tracksObject)) {
            tracksStore.push(tracksObject);
        }
    });

    loadDateButtons();
    callback();
}

/**
 * Load the date selection button onto the DOM
 */
function loadDateButtons() {
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

/**
 * Load all the sessions of a given day into the timeline
 * @param {string} day
 */
function loadTracksToTimeline(day) {

    var dayIndex = _.indexOf(days, day);

    $tracksHolder.empty();
    $unscheduledSessionsHolder.empty();
    $noSessionsInfoBox.show();

    _.each(tracksStore, addTrackToTimeline);

    _.each(sessionsStore[dayIndex], function (session) {
        // Add session elements, but do not broadcast.
        if (!_.isNull(session.top) && !_.isNull(session.track_id) && !_.isNull(session.start_time) && !_.isNull(session.end_time) && !session.hasOwnProperty("isReset")) {
            addSessionToTimeline(session, null, false);
            if(session.title === "RedHat") {
                console.log(session);
            }
        } else {
            addSessionToUnscheduled(session, false, false);
        }
    });

    $tracks = $tracksHolder.find(".track");
    $("[data-toggle=tooltip]").tooltip("hide");
}

function loadData(eventId, callback) {
    $.get("/api/v2/events/" + eventId + "/tracks", function (tracks) {
        $.get("/api/v2/events/" + eventId + "/sessions", function (sessions) {
            processTrackSession(tracks, sessions, callback);
        });
    });
}

/**
 * Initialize the timeline for a given event
 * @param {int} eventId The event ID
 */
function initializeTimeline(eventId) {
    loadData(eventId, function () {
        $(".flash-message-holder").hide();
        $(".scheduler-holder").show();
        initializeInteractables();

    });
}
/**
 * FUNCTIONS THAT ARE TRIGGERED BY EVENTS
 * ======================================
 *
 */

/**
 * Hold the timeline track headers in place while scroll
 */
$(".timeline").scroll(function () {
    var cont = $(this);
    var el = $(cont.find(".track-inner")[0]);
    var elementTop = el.position().top;
    var pos = cont.scrollTop() + elementTop;
    cont.find(".track-header").css("top", pos + "px");
});

/**
 * Handle unscheduled sessions search
 */
$("#sessions-search").valueChange(function (value) {
    var filtered = [];

    if (_.isEmpty(value) || value == "") {
        filtered = unscheduledStore;
    } else {
        filtered = _.filter(unscheduledStore, function (session) {
            return fuzzyMatch(session.title, value);
        });
    }

    filtered = _.sortBy(filtered, "title");
    
    $unscheduledSessionsHolder.html("");

    if (filtered.length == 0) {
        $(".no-sessions-info").show();
    } else {
        $(".no-sessions-info").hide();
        _.each(filtered, function (session) {
            addSessionToUnscheduled(session, true);
        });
    }
});

/**
 * Global document events for date change button, remove button and clear overlaps button
 */
$(document)
    .on("click", ".date-change-btn", function () {
        $(this).addClass("active").siblings().removeClass("active");
        loadTracksToTimeline($(this).text());
    })
    .on("click", ".session.scheduled > .remove-btn", function () {
        addSessionToUnscheduled($(this).parent());
    })
    .on("click", ".clear-overlaps-button", removeOverlaps);

/**
 * Initialize the Scheduler UI on document ready
 */
$(document).ready(function () {
    var eventId = $timeline.data("event-id");
    generateTimeUnits();
    initializeTimeline(eventId);
});
