$( document ).ready(function() {

    var long = $("#longitude").val();
    var lati = $("#latitude").val();
    var labelName = $("#name").val();
    if (lati == "") {
        lati = "51.08150695757747";
    }
    if (long == ""){ long = "17.026073455812494"}
    if (labelName == ""){ labelName = "Type name"}
    var	Lon             = long ;
    var	Lat             = lati;
    var	Zoom            = 14;
    var EPSG4326        = new OpenLayers.Projection( "EPSG:4326" );
    var EPSG900913      = new OpenLayers.Projection("EPSG:900913");

    var	LL              = new OpenLayers.LonLat( Lon, Lat );
    var	XY              = LL.clone().transform( EPSG4326, EPSG900913 );


    var map = new OpenLayers.Map("map",{ projection: EPSG900913});

    //Open Street Maps layer
    map.addLayer(new OpenLayers.Layer.OSM());

    map.setCenter(XY, Zoom);

    var	deftColor     = "#00FF00";
    var	deftIcon      = "/static/admin/img/marker.png";
    var	featureHeight = 32;
    var	featureWidth  = 32;
    var	featureStyle  =	{
        fillColor:      deftColor,
        strokeColor:    deftColor,
        pointRadius:    1,
        externalGraphic:deftIcon,
        graphicWidth:   featureWidth,
        graphicHeight:  featureHeight,
        graphicXOffset: -featureWidth/2,
        graphicYOffset: -featureHeight,
        label:          labelName,
        fontColor:      "#000000",
        fontSize:       "10px",
        fontWeight:     "bold",
        labelAlign:     "rm"
    };

    var	vectorL = new OpenLayers.Layer.Vector(  "Vector Layer", {
                                                styleMap:   new OpenLayers.StyleMap(  featureStyle  )
    });
    map.addLayer( vectorL );


    var	dragVectorC = new OpenLayers.Control.DragFeature(   vectorL, {
                                                            onDrag: function(feature, pixel){

        //Don´t user the position of the pixel or the feature, use the point position instead!
        var point = feature.geometry.components[0];

        var llpoint = point.clone();
        llpoint.transform(  new OpenLayers.Projection(EPSG900913),
                            new OpenLayers.Projection(EPSG4326));
        $("#latitude").val(llpoint.y);
        $("#longitude").val(llpoint.x);

    }});

    map.addControl( dragVectorC );
    dragVectorC.activate();


    var	point       = new OpenLayers.Geometry.Point( XY.lon, XY.lat );
    var	featureOb   = new OpenLayers.Feature.Vector( new OpenLayers.Geometry.Collection([point]) );
    vectorL.addFeatures( [featureOb] );
});