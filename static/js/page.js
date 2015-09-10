var startY;
str = $(".container").html();
$(".container").html(str.replace(/\u200b/ig, "").replace(/&nbsp;/ig,''));
$(".main p").attr('style','');
$(".main span").attr('style','');
//本地存储
$(document).ready(function(){
    var isLogin=sessionStorage.getItem("load");
    if(isLogin){
        $(".download").css({display:"none"});
        $(".all").css({marginTop:"0"})
    }
})
$(".all").css({marginTop:$(".download").css("height")})
str = $(".container").html();
$(".container").html(str.replace(/\u200b/ig, "").replace(/&nbsp;/ig,''));
$(".main p").attr('style','');
$(".main span").attr('style','');
//监听滑动方向
function touchSatrtFunc(e) {
    //evt.preventDefault(); //阻止触摸时浏览器的缩放、滚动条滚动等
    var touch = e.touches[0]; //获取第一个触点
    var x = Number(touch.pageX); //页面触点X坐标
    var y = Number(touch.pageY); //页面触点Y坐标
    //记录触点初始位置
    startY = y;
}
function touchMoveFunc(e) {

    //evt.preventDefault(); //阻止触摸时浏览器的缩放、滚动条滚动等
    var touch = e.touches[0]; //获取第一个触点
    var y = Number(touch.pageY); //页面触点Y坐标
    //判断滑动方向
//      alert(touch)
    if (y - startY > 0) {
        //上下滑动
        $("#navigationSp").slideDown()

    }
}
function ToucheEndFunc(e) {
//        e.preventDefault(); //阻止触摸时浏览器的缩放、滚动条滚动等
    var touch = e.changedTouches[0]; //获取第一个触点
    var y = Number(touch.pageY); //页面触点Y坐标
    if(y-startY<=-7){
        $("#navigationSp").slideUp(200);
    }
}
if (document.addEventListener) {
    document.addEventListener('touchstart', touchSatrtFunc, false);
}
if (document.addEventListener) {
    document.addEventListener('touchmove', touchMoveFunc, false);
}
if (document.addEventListener) {//firefox
    document.addEventListener('touchend', ToucheEndFunc, false);
}
//下载按钮
$(".download>a").click(function(){
    $(".download").slideUp();
    $(".content").css({marginTop:"0"});
    sessionStorage.setItem("load",true);//键值对
})
$(".close").click(function (){
    $(".download").slideUp();
    $(".all").css({marginTop:"0"});
    sessionStorage.setItem("load",true);//键值对
})