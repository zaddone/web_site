var browser = {
    versions: function() {
        var u = navigator.userAgent, app = navigator.appVersion;
        return {//移动终端浏览器版本信息
            trident: u.indexOf('Trident') > -1, //IE内核
            presto: u.indexOf('Presto') > -1, //opera内核
            webKit: u.indexOf('AppleWebKit') > -1, //苹果、谷歌内核
            gecko: u.indexOf('Gecko') > -1 && u.indexOf('KHTML') == -1, //火狐内核
            mobile: !!u.match(/AppleWebKit.*Mobile.*/) || !!u.match(/AppleWebKit/), //是否为移动终端
            ios: !!u.match(/\(i[^;]+;( U;)? CPU.+Mac OS X/), //ios终端
            android: u.indexOf('Android') > -1 || u.indexOf('Linux') > -1, //android终端或者uc浏览器
            iPhone: u.indexOf('iPhone') > -1, //是否为iPhone或者QQHD浏览器
            iPad: u.indexOf('iPad') > -1, //是否iPad
            webApp: u.indexOf('Safari') == -1, //是否web应该程序，没有头部与底部
            weixing: u.indexOf("MicroMessenger") > -1
        };
    }(),
    language: (navigator.browserLanguage || navigator.language).toLowerCase()
}
console.log(browser.versions)
if (browser.versions.ios||browser.versions.iPad||browser.versions.iPhone) {
    if(browser.versions.weixing){
		$("#tanchuang span").text("在Safari中打开")
            $("#tanchuang").show()
        $("#download").on('click', function () {
            $("#tanchuang span").text("在Safari中打开")
            $("#tanchuang").show()
        })
    }else{
    	if ($('#down').attr("show")!='page' ){
    		window.location.href=$('#down').attr("ios")
    	}
        $("#download").attr("href",$('#down').attr("ios"))
    }
}else{
    if(browser.versions.weixing){
		            $("#tanchuang span").text("在浏览器中打开")
            $("#tanchuang").show()
        $("#download").on('click', function () {
            $("#tanchuang span").text("在浏览器中打开")
            $("#tanchuang").show()
        })
    }else{
    	if ($('#down').attr("show")!='page' ){
    		window.location.href= $('#down').attr("android"); 
    	}    	
		
        $("#download").attr("href",$('#down').attr("android"))
    }
}
$("#tanchuang").on('click', function () {
    $(this).hide()
})