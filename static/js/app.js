/**
 * Created with JetBrains WebStorm.
 * User: Administrator
 * Date: 15-9-9
 * Time: 上午11:18
 * To change this template use File | Settings | File Templates.
 */
$(document).ready(function(){
//        alert( document.documentElement.clientHeight)
    $(".banner_img").css({maxHeight:window.innerHeight})
    //轮播
    $('.carousel').carousel();
    var mytime=setInterval (rightmove,3000);
    var c_width=$(".par_cat").css("width");
    $(".cat ul").css({width:4.25*parseInt(c_width)+"px"})
    $(window).resize(function() {
        $(".cat ul")[0].style.marginLeft='0px';
        c_width=$(".par_cat").css("width")
        $(".cat ul").css({width:4.25*parseInt(c_width)+"px"})
    });
    function rightmove(){
        var lb=$(".cat ul")[0];
        if(lb.style.marginLeft ==''){
            lb.style.marginLeft=0;
        }
        lb.style.marginLeft =parseInt (lb.style.marginLeft)-0.25*parseInt(c_width)+'px';
        if(parseInt (lb.style.marginLeft)<-3.25*parseInt(c_width)){
            lb.style.marginLeft='0px';
        }
    }
    $(".par_cat").mouseover(function(){
        clearInterval(mytime);
    } )
    $(".par_cat").mouseout(function(){
        mytime=setInterval (rightmove,3000);
    } )

    $($(".top_back img")[0]).click(function pageScroll(){
//        document.documentElement.scrollTop = document.body.scrollTop =0;
            window.scrollBy(0,-130);
            scrolldelay = setTimeout(pageScroll,50);
            var sTop=document.documentElement.scrollTop+document.body.scrollTop;
            if(sTop==0) clearTimeout(scrolldelay);
            $(".header").slideDown();
        }
    )

    $(".weixin").mouseover(function(){
        $(".showQc").css({visibility:"visible"});
    })
    $(".weixin").mouseout(function(){
        $(".showQc").css({visibility:"hidden"});
    })
})