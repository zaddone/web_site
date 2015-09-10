var mySwiper = new Swiper('.swiper-container', {
    loop:true,
    autoplay: 5000,
    pagination: '.swiper-pagination',
    paginationClickable: true
})


var scrollFunc = function (e) {
    e = e || window.event;
    if (e.wheelDelta) {  //判断浏览器IE，谷歌滑轮事件
        if (e.wheelDelta > 0) { //当滑轮向上滚动时
            $(".header").slideDown(200);
        }
        if (e.wheelDelta < 0) { //当滑轮向下滚动时
            $(".header").slideUp(200);
        }
    } else if (e.detail) {  //Firefox滑轮事件
        if (e.detail> 0) { //当滑轮向下滚动时
            $(".header").slideUp(200)
        }
        if (e.detail< 0) { //当滑轮向上滚动时
            $(".header").slideDown(200)
        }
    }
}
//给页面绑定滑轮滚动事件
if (document.addEventListener) {//firefox
    document.addEventListener('DOMMouseScroll', scrollFunc, false);
}
//滚动滑轮触发scrollFunc方法  //ie 谷歌
window.onmousewheel = document.onmousewheel = scrollFunc;

$(".content p br").replaceWith(" ");
document.onscroll =function aaa(){
    var sTop=document.documentElement.scrollTop+document.body.scrollTop;
    var top=$(".top_back")[0];
    if(sTop>0) {
        top.style.top = "80%"
    }else{
        top.style.top = "1200px"
    }
}

if(window.location.pathname=="/aboutus/"){
    $(".about").css({borderBottom:"1px solid #4E3838",color:"#000",fontsize:"1.1em"})
}
$(".weixin").mouseover(function(){
    $(".showQc").css({visibility:"visible"});
})
$(".weixin").mouseout(function(){
    $(".showQc").css({visibility:"hidden"});
})
