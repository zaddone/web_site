/*!
 * IE10 viewport hack for Surface/desktop Windows 8 bug
 * Copyright 2014-2015 Twitter, Inc.
 * Licensed under MIT (https://github.com/twbs/bootstrap/blob/master/LICENSE)
 */

// See the Getting Started docs for more information:
// http://getbootstrap.com/getting-started/#support-ie10-width

(function () {
  'use strict';

  if (navigator.userAgent.match(/IEMobile\/10\.0/)) {
    var msViewportStyle = document.createElement('style')
    msViewportStyle.appendChild(
      document.createTextNode(
        '@-ms-viewport{width:auto!important}'
      )
    )
    document.querySelector('head').appendChild(msViewportStyle)
  }

})();

var body_width = $("body").width();
console.log(body_width);
if(body_width<=360){
  $(".thumbnail img").height(190);
}else if(body_width<=500){
  $(".thumbnail img").height(255);
}else if(body_width<=768){
  $(".thumbnail img").height(300);
}else if(body_width>1200){
  $(".thumbnail img").height(310);
}
