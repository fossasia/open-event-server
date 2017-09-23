Date.prototype.mmddyyyy = function() {
  var mm = this.getMonth() + 1;
  var dd = this.getDate();
  return [(mm>9 ? '' : '0') + mm, (dd>9 ? '' : '0') + dd, this.getFullYear()].join('/');
};

Date.prototype.hhmm = function() {
  var mm = this.getMinutes() + 1;
  var hh = this.getHours();
  return [(hh>9 ? '' : '0') + hh, (mm>9 ? '' : '0') + mm].join(':');
};


var SESSION_TYPE = {
    id: null,
    name: '',
    length: '00:30'
};

var MICROLOCATION = {
    id: null,
    name: '',
    floor: ''
};

var TRACK = {
    id: null,
    name: '',
    color: '',
    font_color: ''
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
    while(!track.color || track.color === '') {
        track.color = palette.random("800");
    }
    track.font_color = getFontColor(track.color);
    return track;
}

function getFontColor(hex) {
    var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    if(result) {
        var a = 1 - (0.299 * parseInt(result[1], 16) + 0.587 * parseInt(result[2], 16) + 0.114 * parseInt(result[3], 16))/255;
        return (a < 0.5) ? '#000000' : '#ffffff';
    }
    return '#ffffff';
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
    var currentDate = (new Date());
    callForSpeakers.start_date = currentDate.mmddyyyy();
    callForSpeakers.start_time = currentDate.hhmm();
    callForSpeakers.end_date = event.end_time_date;
    callForSpeakers.end_time = event.end_time_time;
    callForSpeakers.timezone = event.timezone;
    return callForSpeakers;
}
