var SESSION_TYPE = {
    id: null,
    name: '',
    length: '00.30'
};

var MICROLOCATION = {
    id: null,
    name: '',
    floor: ''
};

var TRACK = {
    id: null,
    name: '',
    color: ''
};

var CALL_FOR_SPEAKERS = {
    announcement: '',
    start_date: '',
    start_time: '',
    end_date: '',
    end_time: '',
    timezone: current_timezone,
    privacy: 'public',
    hash: cfsHash
};

function getNewTrack(name) {
    var track = _.clone(TRACK);
    track.name = _.isUndefined(name) ? '' : name;
    track.color = palette.random("800");
    track.color = palette.random("800");
    if(!track.color || track.color === '') {
        track.color = palette.random("800");
    }
    return track;
}

function getNewSessionType(name) {
    var sessionType = _.clone(SESSION_TYPE);
    sessionType.name = _.isUndefined(name) ? '' : name;
    return sessionType;
}

function getNewMicrolocation(name) {
    var microlocation = _.clone(MICROLOCATION);
    microlocation.name = _.isUndefined(name) ? '' : name;
    return microlocation;
}


function getCallForSpeakers(event) {
    var callForSpeakers = _.clone(CALL_FOR_SPEAKERS);
    callForSpeakers.end_date = event.end_time_date;
    callForSpeakers.end_time = event.end_time_time;
    callForSpeakers.timezone = event.timezone;
    return callForSpeakers;
}
