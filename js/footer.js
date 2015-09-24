//	contains title, bootstrap, meta, flexslider, modernizr, and custom css
document.write(
    '<footer>'
    +'<div class="container">'
        +'<div class="row-fluid">'
            +'<div class="span12 copyright-outer">'
                +'<div class="row-fluid">'
                    +'<div class="span12 copyright-middle">'
                        +'<div class="row-fluid"><div class="dummy-copyright span12"></div></div>'
                        +'<div class="row-fluid">'
                            +'<div class="span12 copyright">'
                                +'<div class="row-fluid">'
                                    +'<div class="span6 copyright-inner copyright-left">'
                                        +'<span class="st_sharethis" displayText="ShareThis"></span>'
                                        +'<span class="st_facebook" displayText="Facebook"></span>'
                                        +'<span class="st_twitter" displayText="Tweet"></span>'
                                        +'<span class="st_linkedin" displayText="LinkedIn"></span>'
                                        +'<span class="st_pinterest" displayText="Pinterest"></span>'
                                        +'<span class="st_email" displayText="Email"></span>'
                                    +'</div>'
                                    +'<div class="span6 copyright-inner copyright-right">'
                                        +'<!--<div class="copyright-text">Site by</div>-->'
                                        +'<a href="http://radtek.ca/" target=_blank>Radtek Inc.</a> &copy 2012-2015'
                                    +'</div>'
                                +'</div>'
                            +'</div>'
                        +'</div>'
                        +'<div class="row-fluid"><div class="dummy-copyright-bottom span12"></div></div>'
                    +'</div>'
                +'</div>'
            +'</div>'
        +'</div>'
    +'</div>'
+'</footer>'
+'<!--<script src="http://ajax.googleapis.com/ajax/libs/jquery/1/jquery.min.js"></script>-->'
+'<script defer src="js/libs/jquery.flexslider.js"></script>'
+'<!--<script src="js/libs/jquery.easing.js"></script>-->'
+'<!--<script src="js/libs/jquery.mousewheel.js"></script>-->'
+"<script>"
  +"(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){"
  +"(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),"
  +"m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)"
  +"})(window,document,'script','//www.google-analytics.com/analytics.js','ga');"
  +"ga('create', 'UA-38507020-1', 'auto');"
  +"ga('send', 'pageview');"
+"</script>"
+'<script type="text/javascript">'
    +'$(window).load(function(){'
      +'$(\'.flexslider\').flexslider({'
        +'animation: "slide",'
        +'start: function(slider){'
          +'$(\'body\').removeClass(\'loading\');'
        +'}'
      +'});'
    +'});'
  +'</script>'
);



