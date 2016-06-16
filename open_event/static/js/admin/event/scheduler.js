/**
 * Created by Niranjan (@niranjan94) on 23-May-16.
 */

/**
 *  TIME CONFIGURATION & MANIPULATION
 *  =================================
 *
 *  24px === 15 minutes
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
    },
    format: "YYYY-MM-DD HH:mm:ss"
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
var microlocationsStore = [];
var unscheduledStore = [];
var eventId;

/**
 * jQuery OBJECT REFERENCES
 * ========================
 *
 * @type {jQuery|HTMLElement}
 */
var $timeline = $("#timeline");
var $microlocations = $(".microlocation");
var $unscheduledSessionsList = $("#sessions-list");
var $microlocationsHolder = $("#microlocation-container");
var $unscheduledSessionsHolder = $unscheduledSessionsList;
var $noSessionsInfoBox = $("#no-sessions-info");
var $dayButtonsHolder = $("#date-change-btn-holder");
var $addMicrolocationForm = $('#add-microlocation-form');
var $editSessionModal = $('#edit-session-modal');
var $editSessionForm = $("#edit-session-form");

/**
 * TEMPLATE STRINGS
 * ================
 *
 * @type {string}
 */
var microlocationTemplate = $("#microlocation-template").html();
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
        if ($sessionElement.length === 0) {
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
 * @param {Object} [position] Contains position information if the session is changed (microlocation-id and top)
 * @param {boolean} [shouldBroadcast=true]
 */
function addSessionToTimeline(sessionRef, position, shouldBroadcast) {
    var sessionRefObject;
    if (_.isUndefined(position)) {
        sessionRefObject = getSessionFromReference(sessionRef, $unscheduledSessionsHolder);
    } else {
        sessionRefObject = getSessionFromReference(sessionRef, $microlocationsHolder);
    }

    if (!sessionRefObject) {
        logError("addSessionToTimeline", sessionRef);
        return false;
    }

    if ((_.isNull(sessionRefObject.session.microlocation) || _.isNull(sessionRefObject.session.microlocation.id)) && isUndefinedOrNull(position)) {
        addSessionToUnscheduled(sessionRefObject.$sessionElement);
        return;
    }

    var oldMicrolocation = (_.isNull(sessionRefObject.session.microlocation) ? 0 : sessionRefObject.session.microlocation.id);
    var newMicrolocation = null;

    if (!isUndefinedOrNull(position)) {
        sessionRefObject.session.top = position.top;
        sessionRefObject.session.microlocation = {
            id: position.microlocation_id,
            name: position.microlocation_name
        };
        newMicrolocation = position.microlocation_id;
        sessionRefObject.session = updateSessionTime(sessionRefObject.$sessionElement);
        sessionRefObject.$sessionElement.data("session", sessionRefObject.session);
    } else {
        if (isUndefinedOrNull(shouldBroadcast) || shouldBroadcast) {
            sessionRefObject.session = updateSessionTime(sessionRefObject.$sessionElement);
        }
    }


    sessionRefObject.$sessionElement.css({
        "-webkit-transform": "",
        "transform": ""
    }).removeData("x").removeData("y");

    sessionRefObject.$sessionElement.removeClass("unscheduled").addClass("scheduled");

    delete  sessionRefObject.session.start_time.isReset;
    delete  sessionRefObject.session.end_time.isReset;

    sessionRefObject.$sessionElement.data("temp-top", sessionRefObject.session.top);
    sessionRefObject.$sessionElement.css("top", sessionRefObject.session.top + "px");
    sessionRefObject.$sessionElement.css("height", minutesToPixels(sessionRefObject.session.duration) + "px");
    $microlocationsHolder.find(".microlocation[data-microlocation-id=" + sessionRefObject.session.microlocation.id + "] > .microlocation-inner").append(sessionRefObject.$sessionElement);

    sessionRefObject.$sessionElement.ellipsis().ellipsis();

    updateSessionTimeOnTooltip(sessionRefObject.$sessionElement);
    updateColor(sessionRefObject.$sessionElement);

    if (isUndefinedOrNull(shouldBroadcast) || shouldBroadcast) {
        if (!sessionRefObject.newElement) {
            $(document).trigger({
                type: "scheduling:change",
                session: sessionRefObject.session
            });
        }

        $(document).trigger({
            type: "scheduling:recount",
            microlocations: [oldMicrolocation, newMicrolocation]
        });
    }

    _.remove(unscheduledStore, function (sessionTemp) {
        return sessionTemp.id === sessionRefObject.session.id
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

    var sessionRefObject = getSessionFromReference(sessionRef, $microlocationsHolder);
    if (!sessionRefObject) {
        logError("addSessionToUnscheduled", sessionRef);
        return false;
    }

    var oldMicrolocation = (_.isNull(sessionRefObject.session.microlocation) ? 0 : sessionRefObject.session.microlocation.id);

    sessionRefObject.session.top = null;
    sessionRefObject.session.duration = 30;
    sessionRefObject.session.start_time.hours(0).minutes(0);
    sessionRefObject.session.end_time.hours(0).minutes(0);
    sessionRefObject.session.microlocation.id = null;

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
                $(document).trigger({
                    type: "scheduling:change",
                    session: sessionRefObject.session
                });
            }
            $(document).trigger({
                type: "scheduling:recount",
                microlocations: [oldMicrolocation]
            });
        }
        unscheduledStore.push(sessionRefObject.session);
    }
}

/**
 * Update the counter badge that displays the number of sessions under each microlocation
 * @param {array} microlocationIds An array of microlocation IDs to recount
 */
function updateMicrolocationSessionsCounterBadges(microlocationIds) {
    _.each(microlocationIds, function (microlocationId) {
        var $microlocation = $microlocationsHolder.find(".microlocation[data-microlocation-id=" + microlocationId + "] > .microlocation-inner");
        var sessionsCount = $microlocation.find(".session.scheduled").length;
        $microlocation.find(".microlocation-header > .badge").text(sessionsCount);
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
    var $sessionElements = $microlocationsHolder.find(".session.scheduled");
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
 * @param {jQuery} [$microlocation] The microlocation to search in
 * @returns {boolean|jQuery} If no overlap, return false. If overlaps, return the session that's beneath.
 */
function isSessionOverlapping($session, $microlocation) {
    if (isUndefinedOrNull($microlocation)) {
        $microlocation = $session.parent();
    }
    var $otherSessions = $microlocation.find(".session.scheduled");
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
    return !horizontallyBound($microlocations, $sessionElement, 0);
}

/**
 * Check if the session element is over the timeline
 * @param {jQuery} $sessionElement the session element to check
 * @returns {boolean}
 */
function isSessionOverTimeline($sessionElement) {
    try {
        return collision($microlocations, $sessionElement);
    } catch (e) {
        return false;
    }
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
    var mins = pixelsToMinutes($sessionElement.outerHeight(false));
    var topInterval = pixelsToMinutes($sessionElement.data("temp-top"), true);

    var newStartTime = _.cloneDeep(topTime.add(topInterval, 'm'));
    var newEndTime = topTime.add(mins, "m");

    session.duration = mins;
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
 * Add a new microlocation to the timeline
 * @param {object} microlocation The microlocation object containing the details of the microlocation
 */
function addMicrolocationToTimeline(microlocation) {
    var $microlocationElement = $(microlocationTemplate);
    $microlocationElement.attr("data-microlocation-id", microlocation.id);
    $microlocationElement.attr("data-microlocation-name", microlocation.name);
    $microlocationElement.find(".microlocation-header").html(microlocation.name + "&nbsp;&nbsp;&nbsp;<span class='badge'>0</span>");
    $microlocationElement.find(".microlocation-inner").css("height", time.unit.count * time.unit.pixels + "px");
    $microlocationsHolder.append($microlocationElement);
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
    $microlocationsHolder.css("height", timeUnitsCount * time.unit.pixels);
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

    $microlocations = $microlocationsHolder.find(".microlocation");

    interact(".session")
        .draggable({
            // enable inertial throwing
            inertia: false,
            // enable autoScroll
            autoScroll: {
                container: $microlocationsHolder[0],
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

                $sessionElement.data("temp-top", roundOffToMultiple($sessionElement.offset().top - $(".microlocations.x1").offset().top));

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
                $(document).trigger({
                    type: "scheduling:change",
                    session: updateSessionTime($sessionElement)
                });

            }
        });

    interact(".microlocation-inner").dropzone({
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
            var $microlocationDropZone = $(event.target);

            $microlocationDropZone.removeClass("drop-active").removeClass("drop-now");

            addSessionToTimeline($sessionElement, {
                microlocation_id: parseInt($microlocationDropZone.parent().attr("data-microlocation-id")),
                microlocation_name: $microlocationDropZone.parent().attr("data-microlocation-name"),
                top: $sessionElement.data("temp-top")
            });

            var isColliding = isSessionOverlapping($sessionElement, $microlocationDropZone);
            if (!isColliding) {
                updateSessionTime($sessionElement);
            } else {
                createSnackbar("Session cannot be dropped onto another sessions.", "Try Again");
                addSessionToUnscheduled($sessionElement);
            }

        },
        ondropdeactivate: function (event) {
            var $microlocationDropZone = $(event.target);
            var $sessionElement = $(event.relatedTarget);
            $microlocationDropZone.removeClass("drop-now").removeClass("drop-active");
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
 * This callback called after sessions and microlocations are processed.
 * @callback postProcessCallback
 */
/**
 * Process the microlocations and sessions data loaded from the server into in-memory data stores
 * @param {object} microlocations The microlocations json object
 * @param {object} sessions The sessions json object
 * @param {postProcessCallback} callback The post-process callback
 */
function processMicrolocationSession(microlocations, sessions, callback) {
    var topTime = moment.utc({hour: time.start.hours, minute: time.start.minutes});
    _.each(sessions, function (session) {
        session = _.cloneDeep(session);

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

        session.start_time = startTime;
        session.end_time = endTime;
        session.duration = Math.abs(duration.asMinutes());
        session.top = top;

        var dayIndex = _.indexOf(days, dayString);

        if (_.isArray(sessionsStore[dayIndex])) {
            sessionsStore[dayIndex].push(session);
        } else {
            sessionsStore[dayIndex] = [session]
        }
    });

    _.each(microlocations, function (microlocation) {
        if (!_.includes(microlocationsStore, microlocation)) {
            microlocationsStore.push(microlocation);
        }
    });

    microlocationsStore = _.sortBy(microlocationsStore, "name");
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
        if (index === 0) {
            $dayButton.addClass("active");
        }
        $dayButton.text(day);
        $dayButtonsHolder.append($dayButton)
    });
    loadMicrolocationsToTimeline(sortedDays[0]);
}

/**
 * Load all the sessions of a given day into the timeline
 * @param {string} day
 */
function loadMicrolocationsToTimeline(day) {

    var dayIndex = _.indexOf(days, day);

    $microlocationsHolder.empty();
    $unscheduledSessionsHolder.empty();
    $noSessionsInfoBox.show();

    _.each(microlocationsStore, addMicrolocationToTimeline);

    _.each(sessionsStore[dayIndex], function (session) {
        // Add session elements, but do not broadcast.
        if (!_.isNull(session.top) && !_.isNull(session.microlocation) && !_.isNull(session.microlocation.id) && !_.isNull(session.start_time) && !_.isNull(session.end_time) && !session.hasOwnProperty("isReset")) {
            addSessionToTimeline(session, null, false);
        } else {
            addSessionToUnscheduled(session, false, false);
        }
    });

    $microlocations = $microlocationsHolder.find(".microlocation");
    $("[data-toggle=tooltip]").tooltip("hide");
}

function loadData(eventId, callback) {
    api.microlocations.get_microlocation_list({event_id: eventId}, function (microlocationsData) {
        api.sessions.get_session_list({event_id: eventId}, function (sessionData) {
            processMicrolocationSession(microlocationsData.obj, sessionData.obj, callback);
        })
    });
}

/**
 * Initialize the timeline for a given event
 * @param {int} eventId The event ID
 */
function initializeTimeline(eventId) {
    initializeSwaggerClient(function () {
        loadData(eventId, function () {
            $(".flash-message-holder").hide();
            $(".scheduler-holder").show();
            initializeInteractables();
        });
    });
}
/**
 * FUNCTIONS THAT ARE TRIGGERED BY EVENTS
 * ======================================
 *
 */

/**
 * Hold the timeline microlocation headers in place while scroll
 */
$(".timeline").scroll(function () {
    var cont = $(this);
    var el = $(cont.find(".microlocation-inner")[0]);
    var elementTop = el.position().top;
    var pos = cont.scrollTop() + elementTop;
    cont.find(".microlocation-header").css("top", pos + "px");
});

/**
 * Handle unscheduled sessions search
 */
$("#sessions-search").valueChange(function (value) {
    var filtered = [];

    if (_.isEmpty(value) || value === "") {
        filtered = unscheduledStore;
    } else {
        filtered = _.filter(unscheduledStore, function (session) {
            return fuzzyMatch(session.title, value);
        });
    }

    filtered = _.sortBy(filtered, "title");

    $unscheduledSessionsHolder.html("");

    if (filtered.length === 0) {
        $(".no-sessions-info").show();
    } else {
        $(".no-sessions-info").hide();
        _.each(filtered, function (session) {
            addSessionToUnscheduled(session, true);
        });
    }
});

$addMicrolocationForm.submit(function (event) {
    event.preventDefault();
    var payload = {
        "room": $addMicrolocationForm.find("input[name=room]").val(),
        "latitude": parseFloat($addMicrolocationForm.find("input[name=latitude]").val()),
        "name": $addMicrolocationForm.find("input[name=name]").val(),
        "longitude": parseFloat($addMicrolocationForm.find("input[name=longitude]").val()),
        "floor": parseInt($addMicrolocationForm.find("input[name=floor]").val())
    };

    api.microlocations.post_microlocation_list({event_id: eventId, payload: payload}, function (success) {
        addMicrolocationToTimeline(success.obj);
        $addMicrolocationForm.find(".modal").modal("hide");
        $addMicrolocationForm.find("input, textarea").val("");
        createSnackbar("Microlocation has been created successfully.");
    }, function (error) {
        console.log('failed with the following: ' + error.statusText);
        createSnackbar("An error occurred while creating microlocation.", "Try Again", function () {
            $addMicrolocationForm.trigger("submit");
        });
    });
});

$(".export-png-button").click(function () {
    html2canvas($timeline[0], {
        onrendered: function (canvas) {
            canvas.id = "generated-canvas";
            canvas.toBlob(function (blob) {
                saveAs(blob, "timeline.png");
            });
        }
    });
});

/**
 * Global document events for date change button, remove button and clear overlaps button
 */
$(document)
    .on("click", ".date-change-btn", function () {
        $(this).addClass("active").siblings().removeClass("active");
        loadMicrolocationsToTimeline($(this).text());
    })
    .on("click", ".session.scheduled > .remove-btn", function () {
        addSessionToUnscheduled($(this).parent());
    })
    .on("click", ".session.scheduled > .edit-btn", function () {
        var $sessionElement = $(this).parent();
        var session = $sessionElement.data("session");
        $editSessionForm.bindObject(session, time.format);
        $editSessionModal.modal('show');
    })
    .on("click", ".clear-overlaps-button", removeOverlaps);

$(".date-picker").daterangepicker({
    "singleDatePicker": true,
    "showDropdowns": true,
    "timePicker": true,
    "timePicker24Hour": true,
    "startDate": $editSessionModal.data("start-date"),
    locale: {
        format: time.format
    }
});

$editSessionForm.submit(function () {
    var session = $editSessionForm.data("object");
    session.start_time = moment.utc($editSessionForm.find("input[name=start_time]").val());
    session.end_time = moment.utc($editSessionForm.find("input[name=end_time]").val());
    session.title = $editSessionForm.find("input[name=title]").val();
    session.long_abstract = $editSessionForm.find("input[name=long_abstract]").text();
    session.short_abstract = $editSessionForm.find("input[name=short_abstract]").val();
    $(document).trigger({
        type: "scheduling:change",
        session: session
    });
    $editSessionModal.modal("hide");
});

/**
 * Initialize the Scheduler UI on document ready
 */
$(document).ready(function () {
    eventId = parseInt($timeline.data("event-id"));
    generateTimeUnits();
    initializeTimeline(eventId);
});

$(document).on("scheduling:change", function (e) {

    // Make a deep clone of the session object
    var session = _.cloneDeep(e.session);
    var session_id = session.id;

    // Format the payload to match API requirements
    session.start_time = session.start_time.format(time.format);
    session.end_time = session.end_time.format(time.format);
    session.track_id = _.isNull(session.track.id) ? 0 : session.track.id;
    session.level_id = _.isNull(session.level.id) ? 0 : session.level.id;
    session.format_id = _.isNull(session.format.id) ? 0 : session.format.id;
    session.language_id = _.isNull(session.language.id) ? 0 : session.language.id;
    session.microlocation_id = _.isNull(session.microlocation.id) ? null : session.microlocation.id;
    session.speaker_ids = _.map(session.speakers, 'id');

    // Clean up the payload
    delete session.track;
    delete session.level;
    delete session.format;
    delete session.language;
    delete session.speakers;
    delete session.microlocation;
    delete session.duration;
    delete session.top;
    delete session.id;

    api.sessions.put_session({event_id: eventId, session_id: session_id, payload: session}, function (success) {
        createSnackbar("Changes have been saved.", "Dismiss", null, 1000);
    }, function (error) {
        createSnackbar("An error occurred while saving the changes.", "Try Again", function () {
            $(document).trigger({
                type: "scheduling:change",
                session: e.session
            });
        });
    });
});
