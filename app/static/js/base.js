$(document).ready(function() {
      $('#simple-menu').sidr();
    });
    $('sdir').swipe( {
        //Single swipe handler for left swipes
        swipeLeft: function () {
            $.sidr('close', 'sidr-main');
        },
        swipeRight: function () {
            $.sidr('open', 'sidr-main');
        },
        //Default is 75px, set to 0 for demo so any distance triggers swipe
        threshold: 45
    });
        window.onscroll = function () {
        if (document.documentElement.scrollTop + document.body.scrollTop > 100) {
            document.getElementById("top-place-button").style.display = "block";
        }
        else {
            document.getElementById("top-place-button").style.display = "none";
        }
    }