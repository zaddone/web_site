if($("body").is(".swiper-container")){
var mySwiper = new Swiper('.swiper-container', {
    loop:true,
    autoplay: 3000,
    pagination: '.swiper-pagination',
    paginationClickable: true,
})
}
$(function () {
    $("#showQrcode").hover(function () {
        var posTop = $(this).position().top;
        var posleft = $(this).position().left;
        $(".showQc").css({top:posTop-100,left:posleft}).show()
    }, function () {
        $(".showQc").hide()
    })
//$("#listTagForm").on('click','a', function () {
//    var thisNmae = $(this).attr("name");
//    var thisVal = $(this).attr("value");
//    var lodVal =$("input:hidden[name="+thisNmae+"]").val();
//    if(lodVal.indexOf(thisVal)!=-1){
//        $("input:hidden[name="+thisNmae+"]").val(replaceString(lodVal,thisVal,""))
//    }else{
//        if(lodVal.length==0){
//            $("input:hidden[name="+thisNmae+"]").val(thisVal);
//        }else{
//            $("input:hidden[name="+thisNmae+"]").val(lodVal+","+thisVal)
//        }
//    }
//    $("#listTagForm").submit();
//})
/*
 replaceString �����������滻�����ֵ���͸�ʽ�����ã�Ĭ�����Զ��ŷָ�������ǿ��Դ���4��ֵ�����ָ���ŵ����Ǳ��룩
 a==���滻�ַ�
 b==���滻���ַ�
 c==�滻���ַ�,���Ϊ�ձ�ʾɾ���滻���ַ�
 */
function replaceString(a,b,c){
    console.log(arguments)
    a = a.split(",");
    var d = [];
    for(var i=0;i< a.length;i++){
        if(a[i]==b){
            if($.trim(c).length !=0){
                d.push(c)
            }
        }else{
            d.push(a[i])
        }
    }
    return d.join(",");
}
    /*
        �б�ҳȥ������|ǰ�������
     */
$("#listContent h2").each(function () {
    if ($(this).text().indexOf("|") != -1) {
        var newtext = $(this).text().substr($(this).text().indexOf("|") + 1);
        $(this).text($.trim(newtext))
    }
})
})
    /*
     GetRequest()��ȡget����Ĳ���
     ����ֵ��Object����
     */
    function GetRequest() {
        var url = location.search; //��ȡurl��"?"�����ִ�
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
    if($("body").is("#list_pc")){
    var range = 200;             
    var maxnum = 20; 
    var num = 1;
    var totalheight = 0;
        var main = $("#listContent");
    $(window).scroll(function(){
        var srollPos = $(window).scrollTop(); 
        totalheight = parseFloat($(window).height()) + parseFloat(srollPos);
        if(($(document).height()-range) <= totalheight  && num != maxnum) {
        	alert(totalheight)
            var newData = GetRequest()
            newData.json =1;
            newData.page=num+1;
            $.ajax({
                url:"",
                type:"get",
                data:newData,
                async:false,
                success: function (data) {
                    var _html="";
                    for(var i=0;i<data.list.length;i++){
                        var a = data.list[i];
                        _html+="<div class='col-lg-4 col-md-4 col-sm-6 col-xd-12 listDiv'>" +
                            "<div class='listMain'>"+
                            "<img src='"+a.imgs[0]+"' alt='"+a.title+"'/>" +
                            "<h2>"+a.title+"</h2>" +
                            "<p>"+a.address+"</p>" +
                            "</div>" +
                            "</div>"
                    }
                    main.append(_html);
                    num++;
                }
            })
        }
    });
    }
*/
$(".classList-1 a").each(function(i){
    $($(".classList-1 a")[i]).click(function(){
        console.log(  $($(".classList-1 a")[i]).html())
    })

    $(".classList-1 a")[i].href=""
})