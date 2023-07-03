function getNowFormatDate() {
	var nowDate = new Date();
	var year = nowDate.getFullYear();
	var month = nowDate.getMonth() + 1 < 10 ? "0" + (nowDate.getMonth() + 1)
			: nowDate.getMonth() + 1;
	var date = nowDate.getDate() < 10 ? "0" + nowDate.getDate() : nowDate
			.getDate();
	var hour = nowDate.getHours() < 10 ? "0" + nowDate.getHours() : nowDate
			.getHours();
	var minute = nowDate.getMinutes() < 10 ? "0" + nowDate.getMinutes()
			: nowDate.getMinutes();
	var second = nowDate.getSeconds() < 10 ? "0" + nowDate.getSeconds()
			: nowDate.getSeconds();
	return year + "-" + month + "-" + date + " " + hour + ":" + minute + ":"
			+ second;
}

$(function() {
	var time = getNowFormatDate();
	$('#P_Time').val(time);

	var radio = "";
	$.get("/pay/getPayType",function(obj) {
		$.each(obj.data,function(i, item) {
			if (item.pay_model == "2") {
                radio = radio
                    + "<label>"
					+ "<div class='f_m2'><p><img src='images/"+item.icon+".jpg' />";
					radio = radio + "<span>app支付</span><em>自动跳转到app</em></p>";
				radio = radio + "<input type='radio' onclick=\"rechargeLimit();\" name='bank_code' class='regular-radio' value='"+ item.item_code +"'/>"
						+ "<label for='radio-1-2'></label></div>";
			}
		});
		$("#redioTd").after(radio);
		if(radio != ""){
			$('input[name="bank_code"]').get(0).checked = true;
			rechargeLimit();
		}
	});
})

function rechargeLimit() {

	var payWay = $("input[name='bank_code']:checked").val();

	$.get("/pay/getPayTypeLimit", {payType : payWay}, function(obj) {
		//$("#coin").attr("placeholder", obj);
    	$('#saveLimit').val(obj);
    	var limitNumbers = obj.split(",");
        $('#coin').attr("placeholder","存款额度在"+limitNumbers[0]+"~"+limitNumbers[1]);
		
	});

}

function btnOK_zf_onclick() {
	var username = $("#username").val();
	var usern = /^[a-zA-Z0-9]{1,}$/;
	if (!usern.test(username)) {
        alert('会员帐号只能由数字、字母组成!');
		return false;
	}
	var coin = $("#coin").val();
	var bankck = $('input[name="bank_code"]:checked').val();
	var rusername = $("#rusername").val();
	if (username == null || username == "") {
        alert("[提示]用户名不能为空！");
		$("#username").focus();
		return false;
	}
	if (rusername == null || rusername == "" || rusername != username) {
        alert("[提示]2次用户输入不一致！");
		$("#rusername").focus();
		return false;
	}
	if (bankck == null || bankck == "") {
        alert("[提示]支付类型不能为空！");
		return false;
	}
	if (isNaN(coin)) {
        alert("[提示]存款额度非有效数字！");
		$("#coin").focus();
		return false;
	}

	if(!isMoney(coin)){
			alert("[提示]存款额度非有效数字！");
			$("#coin").focus();
			return false;
	}
	
	var saveLimit = $('#saveLimit').val().split(",");
	if(parseFloat(coin)<parseFloat(saveLimit[0])||parseFloat(coin)>parseFloat(saveLimit[1])){
		alert("[提示]存款额度在"+saveLimit[0]+"~"+saveLimit[1]);
		$("#coin").focus();
		//return false;
	}
	
//	if (coin < 10) {
//        alert("[提示]10元以上才能存款！");
//		$("#coin").focus();
//		return false;
//	}
//	if (coin > 50000) {
//        alert("[提示]存款金额不能超过50000！");
//		$("#coin").focus();
//		return false;
//	}
	var createTime = $('#P_Time').val();
	$("#loadingDiv").show();
    var paramO = {
        backcode : bankck,
        username : username,
        amount : coin,
        applyDate : createTime,
        userIp : returnCitySN["cip"],
    }
    var dataP = {
        url:"/pay/server",
        param:paramO
    }
    postcall(dataP);
}

function isMoney(s) { 
	var regu = /^([1-9][\d]{0,7}|0)(\.[\d]{1,2})?$/;
	var re = new RegExp(regu); 
	if (re.test(s)) { 
		return true; 
	} else { 
		return false; 
	} 
}

function postcall(data) {
    var tempform = document.createElement("form");
    tempform.action = data.url;
    tempform.method = "post";
    tempform.header_text = "application/x-www-form-urlencoded";
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