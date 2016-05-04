$( document ).ready(function() {
        console.log("test");
        $("a").click( function() {
            console.log("test");
            $(this).addClass("active").siblings().removeClass("active");
        });

});