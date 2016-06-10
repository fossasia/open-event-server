/**
 * Created by Niranjan on 09-Jun-16.
 */

/**
 * A Swagger Client to access the API.
 * @doc https://github.com/swagger-api/swagger-js
 */
$.getScript("/static/admin/lib/swagger-js/browser/swagger-client.min.js", function () {
    // Full URL is necessary for proper port handling -@niranjan94
    var swaggerConfigUrl = window.location.protocol + "//" + window.location.host + "/api/v2/swagger.json";
    window.api = new SwaggerClient({
        url: swaggerConfigUrl,
        success: function () {
            $(document).trigger("swagger:loaded");
        }
    });
});
