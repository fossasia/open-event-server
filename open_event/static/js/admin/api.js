/**
 * Created by Niranjan on 09-Jun-16.
 */

/**
 * A Swagger Client to access the API.
 * @doc https://github.com/swagger-api/swagger-js
 */
// Full URL is necessary for proper port handling -@niranjan94
var swaggerConfigUrl = window.location.protocol + "//" + window.location.host + "/api/v2/swagger.json";
window.swagger_loaded = false;
function initializeSwaggerClient(callback) {
    if (!window.swagger_loaded) {
        window.api = new SwaggerClient({
            url: swaggerConfigUrl,
            success: function () {
                window.swagger_loaded = true;
                if (callback) {
                    callback();
                }

            }
        });
    } else {
        if (callback) {
            callback();
        }
    }
}
initializeSwaggerClient();
