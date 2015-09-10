/**
 * Created with JetBrains WebStorm.
 * User: Administrator
 * Date: 15-9-7
 * Time: 上午9:52
 * To change this template use File | Settings | File Templates.
 */
//详情宽度
var w=$(".details").css("width");
var height;

//浏览器可视宽度
var a=document.body.offsetWidth;
//container宽度
var b=$(".container").css("width")
var c=(a-parseInt(b))/2;
//猜你喜欢的left
var left=parseInt(w)+c+50;
$(".guess_like").css({left:left+"px"});
$(".top_back").css({left:left+320+"px"})
$(window).resize(function() {
    height= document.body.scrollHeight;
    l=$(".navigation").css("marginLeft")
    w=$(".details").css("width")
    a=document.body.offsetWidth;
    b=$(".container").css("width")
    c=(a-parseInt(b))/2
    left=parseInt(w)+c+50
    $(".guess_like").css({left:left+"px"});
    $(".top_back").css({left:left+320+"px"})
});

var elm = $(".guess_2");
var width=$(".guess_like").css("width");
$(function() {
    var startPos = $(elm).offset().top;
    $.event.add(window, "scroll", function() {
        height= document.body.scrollHeight;
        var p = $(window).scrollTop();
        if(p>height-1000){

            $(elm).css({position:"absolute",top:""})
        }
        $(elm).css('position',((p) > startPos)&&((p) < height-1000) ? 'fixed' : 'absolute');
        $(elm).css('top',((p) > startPos)&&((p) < height-1000) ? '0px' : '');
        $(elm).css('left',((p) > startPos)&&((p) < height-1000) ? 'left' : 'left');
        $(elm).css('width',((p) > startPos)&&((p) < height-1000) ? parseInt(width)*0.9+'px' : '');
        $(".guess_1").css('opacity',((p) > startPos)&&((p) < height-1000) ? '0' : '');
    });
});

$($(".top_back img")[0]).click(function pageScroll(){
//        document.documentElement.scrollTop = document.body.scrollTop =0;
        window.scrollBy(0,-500);
        scrolldelay = setTimeout(pageScroll,50);
        var sTop=document.documentElement.scrollTop+document.body.scrollTop;
        if(sTop==0) clearTimeout(scrolldelay);
        $(".header").slideDown();
    }
)
$(".weixin").mouseover(function(){
//    $(".showQc").css("")
    $(".showQc").css({visibility:"visible"});
})
$(".weixin").mouseout(function(){
    $(".showQc").css({visibility:"hidden"});
})