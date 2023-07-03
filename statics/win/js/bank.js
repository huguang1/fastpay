$(function() {
    //查询所有银行
    var param=window.location.href.split("=")[1];
    var js=JSON.parse(decodeURIComponent(param));
    $("#username").html(js.username);
    $("#amount").html(js.amount);
    $.get("/pay/listBank",{username:js.username,itemCode:'CYBER_BANK',model:js.model},function(data){
        var html="";
        for(var i=0;i<data.length;i++){
            html+='<li onclick="changeStyle(this)"payId="'+data[i].id+'" bank="'+data[i].bankCode+'"><a href="javascript:;"><img src="win/images/bankimg/JR_'+data[i].bankCode+'.png"></a></li>';
        }
        $(".wycon ul").html(html);
    });
});


//绑定点击的样式修改
function changeStyle(obj){
    $(obj).addClass('on').siblings().removeClass('on')
}
//返回首页
function retIndex(){
    window.location.href='index.html';
}
//提交数据
function submit(){
    var bank=$("ul .on").attr("bank");
    var payId=$("ul .on").attr("payId");
    if(typeof(bank) =="undefined"||typeof(payId) =="undefined"){
        layer.alert("请选择银行");
        return;
    }
    var param=window.location.href.split("=")[1];
    var paramO=JSON.parse(decodeURIComponent(param));
    paramO.bankCode=bank;
    paramO.payInfoId=payId;
    var dataP = {
        url:"/pay/server",
        param:paramO
    }
    postcall(dataP);
}

function postcall(data) {
    var tempform = document.createElement("form");
    tempform.action = data.url;
    tempform.method = "post";
    tempform.style.display = "none"
    for ( var x in data.param) {
        var opt = document.createElement("input");
        opt.type = "hidden";
        opt.name = x;
        opt.value = data.param[x];
        tempform.appendChild(opt);
    }
    var opt = document.createElement("input");
    opt.type = "submit";
    tempform.appendChild(opt);
    document.body.appendChild(tempform);
    tempform.submit();
    document.body.removeChild(tempform);
}