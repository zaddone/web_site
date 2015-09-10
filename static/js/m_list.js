/**
 * Created with JetBrains WebStorm.
 * User: Administrator
 * Date: 15-8-29
 * Time: 下午2:48
 * To change this template use File | Settings | File Templates.
 */
var H=document.documentElement.clientHeight;
var leng=$(".pagination li").length
for(var i=0;i<leng;i++){
    if($($(".pagination li a span")[i]).html()!="上一页"&&$($(".pagination li a span")[i]).html()!="下一页"){
        $($(".pagination li")[i]).css({display:"none"})
    }
}
var h=$("header").css("height");
$(".content").css({marginTop:h})


var list_length=$(".listContent").length
if(list_length<2){
    $("footer").css({position:"fixed",bottom:"0",left:"0"})
}
$("#navigation a").each(function () {
    var inUrl = $(this).attr("href")
    $(this).attr("href",inUrl+window.location.search)
})
//获取当前城市
$.ajax({
    type:'get',
    url :"http://site.xiaorizi.me/test_page/",
    dataType : 'jsonp',
    data:{json:1},
    jsonp:'callback',
    jsonpCallback:"call",
    success  : function(data) {
        var cityname=data.city.retData.city;
        console.log(cityname);
        $(".Domestic li a").each(function(i){
//            console.log(window.location.href)
            if(window.location.href=="http://m.xiaorizi.me/"){
                if(cityname==$($(".Domestic li a")[i]).html()){
                    var citytitle=$(".Domestic li a")[i].href;
                    console.log(citytitle)
                    location.href=citytitle;

                }
            }
        })
    },
    error : function() {
        alert('fail');
    }
})
/*
 GetRequest()获取get传输的参数
 返回值：Object对象
 */
function GetRequest() {
    var url = location.search; //获取url中"?"符后的字串
    var theRequest = new Object();
    if (url.indexOf("?") != -1) {
        var str = url.substr(1);
        strs = str.split("&");
        for(var i = 0; i < strs.length; i ++) {
            theRequest[strs[i].split("=")[0]]=unescape(strs[i].split("=")[1]);
        }
    }
    return theRequest;
}
/*
 下拉滚动到一定位置加载页面
 通过异步请求达到每次只请求一次的效果
 */
var range = 0;             //距下边界长度/单位px
var maxnum = 20;            //设置加载最多次数
var num = 1;
var totalheight = 0;
var main = $("#list_main");                     //主体元素
var startY;
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
        //下滑动
        $("#navigationSp").slideDown();

    }
}
function ToucheEndFunc(e) {
//        e.preventDefault(); //阻止触摸时浏览器的缩放、滚动条滚动等
    var touch = e.changedTouches[0]; //获取第一个触点
    var y = Number(touch.pageY); //页面触点Y坐标
    if(y-startY<=-8){
        $("#navigationSp").slideUp(200);
//            alert(y-startY)
    }
}
var slider=document.getElementById("slider")
if (document.addEventListener) {//firefox
    slider.addEventListener('touchstart', touchSatrtFunc, false);
}
if (document.addEventListener) {//firefox
    slider.addEventListener('touchmove', touchMoveFunc, false);
}
if (document.addEventListener) {//firefox
    slider.addEventListener('touchend', ToucheEndFunc, false);
}
//下载按钮
$(".download>a").click(function(){
    $(".download").css({display:"none"});
    $(".content").css({marginTop:"45px"});
    sessionStorage.setItem("load",true);//键值对
})
$(".close").click(function (){
    $(".tag_list").css({height:H-45+"px"});
    $(".download").css({display:"none"});
    $(".content").css({marginTop:"45px"});
    sessionStorage.setItem("load",true);//键值对
})