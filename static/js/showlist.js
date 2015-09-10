/**
 * Created with JetBrains WebStorm.
 * User: Administrator
 * Date: 15-9-9
 * Time: 上午11:21
 * To change this template use File | Settings | File Templates.
 */
    $(document).ready(function(){
var isLoad=sessionStorage.getItem("load");
var isLogin=sessionStorage.getItem("find_city");
if(isLoad&&(window.location.pathname=="/")){
    location.href=isLogin;
}else if(window.location.pathname=="/"){
    $.ajax({
        type:'get',
        url :"/find_city/",
        dataType : 'jsonp',
        data:{json:1},
        jsonp:'callback',
        jsonpCallback:"call",
        success  : function(data) {
            console.log(data);
            var cityname=data.city.retData.city;
            $(".city_list a").each(function(i){
                if(cityname==$($(".city_list a")[i]).html()){
                    var citytitle=$(".city_list a")[i].href;
                    i
                    location.href=citytitle;
                    sessionStorage.setItem("load",true);//键值对
                    sessionStorage.setItem("find_city",citytitle);//键值对
                }
            })
        },
        error : function() {
            alert('fail');
        }
    })
}
//$($(".cat_list ul")[0]).css({borderBottom:"1px solid #E8E8E8"})
$($(".top_back img")[0]).click(function pageScroll(){
//        document.documentElement.scrollTop = document.body.scrollTop =0;
        window.scrollBy(0,-130);
        scrolldelay = setTimeout(pageScroll,50);
        var sTop=document.documentElement.scrollTop+document.body.scrollTop;
        if(sTop==0) clearTimeout(scrolldelay);
        $(".header").slideDown();
    }
)
$(".xrz").mouseover(function(){
    $(".wx").show();
    $(".wx").animate({
        top:"71%",
        width:"140px"
    },200)
})
$(".xrz").mouseout(function(){
    $(".wx").fadeOut();
    $(".wx").animate({
        top:"85%",
        width:"15px"
    },100)
})
$(".city span").click(function (){
    $(".cat_list").slideUp(200)
    $(".city_list").slideToggle(200)
})
$(".cat span").click(function (){
    $(".city_list").slideUp(200)
    $(".cat_list").slideToggle(200)
})
$(".lazy").lazyload({threshold : 0 ,
    effect:"show",
    placeholder : "/images/prey.jpg",
    event:"scroll"
});
        $(".city_list,.cat_list").mouseleave(function(){
            $(".city_list").slideUp(200);
            $(".cat_list").slideUp(200)
        })
})