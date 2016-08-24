/**
 * Created by Niranjan on 14-Jun-16.
 */
var summernoteConfig = {
    toolbar: [
        ['style', ['bold', 'italic', 'underline', 'clear']],
        ['insert', ['link']],
        ['para', ['ul', 'ol']]
    ],
    popover: {
        link: [
            ['link', ['linkDialogShow', 'unlink']]
        ]
    },
    height: 150,
    disableDragAndDrop: true,
    styleWithSpan: false
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

/**
 * A simple function to create a material design Snackbar with an action button
 * @param {string} message The message to be displayed
 * @param {string} [actionText=Dismiss] The action text to be displayed
 * @param {callback} [action] The callback to execute when pressing the action button
 * @param {number} [delay=5000] The delay for the snackbar
 */
var createSnackbar = (function () {
    var previous = null;

    /**
     *
     */
    return function (message, actionText, action, delay) {
        if (previous) {
            previous.dismiss();
        }

        if (typeof actionText === 'undefined' || actionText == null) {
            actionText = "Dismiss";
        }

        if (typeof delay === 'undefined' || delay == null) {
            delay = 5000;
        }
        var snackbar = document.createElement('div');
        snackbar.className = 'paper-snackbar';
        snackbar.dismiss = function () {
            this.style.opacity = 0;
        };
        var text = document.createTextNode(message);
        snackbar.appendChild(text);
        if (actionText) {
            var hasAction = true;
            if (!action) {
                action = snackbar.dismiss.bind(snackbar);
                hasAction = false;
            }
            var actionButton = document.createElement('button');
            actionButton.className = 'action';
            actionButton.innerHTML = actionText;
            if (hasAction) {
                actionButton.addEventListener('click', function () {
                    action();
                    snackbar.dismiss();
                    snackbar.dismiss.bind(snackbar);
                });
            } else {
                actionButton.addEventListener('click', action);
            }

            snackbar.appendChild(actionButton);
        }
        setTimeout(function () {
            if (previous === this) {
                previous.dismiss();
            }
        }.bind(snackbar), delay);

        snackbar.addEventListener('transitionend', function (event, elapsed) {
            if (event.propertyName === 'opacity' && this.style.opacity == 0) {
                window.snackbar_elapsed = elapsed;
                this.parentElement.removeChild(this);
                if (previous === this) {
                    previous = null;
                }
            }
        }.bind(snackbar));

        previous = snackbar;
        document.body.appendChild(snackbar);
        window.snackbar_bottom = getComputedStyle(snackbar).bottom;
        snackbar.style.bottom = '0px';
        snackbar.style.left = '0px';
        snackbar.style.opacity = 1;
    };
})();


$.oauthpopup = function(options)
{
    options.windowName = options.windowName ||  'ConnectWithOAuth'; // should not include space for IE
    options.windowOptions = options.windowOptions || 'location=0,status=0,width=800,height=400';
    options.callback = options.callback || function(){ window.location.reload(); };
    var that = this;
    that._oauthWindow = window.open(options.path, options.windowName, options.windowOptions);
    that._oauthInterval = window.setInterval(function(){
        if (that._oauthWindow.closed) {
            window.clearInterval(that._oauthInterval);
            options.callback();
        }
    }, 1000);

    var responsePoll = setInterval(function() {
        try {
            if(typeof that._oauthWindow.oauth_response !== 'undefined') {
                window.oauth_response = that._oauthWindow.oauth_response;
                clearInterval(responsePoll);
            }
        }
        catch (error) { }
    }, 250);
};
