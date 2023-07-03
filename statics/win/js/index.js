$(function($) {
	pageInit();
});

function pageInit() {
	browserRedirect();
	loadNotify();
}

function browserRedirect() {
	var sUserAgent = navigator.userAgent.toLowerCase();
	var bIsIpad = sUserAgent.match(/ipad/i) == "ipad";
	var bIsIphoneOs = sUserAgent.match(/iphone os/i) == "iphone os";
	var bIsMidp = sUserAgent.match(/midp/i) == "midp";
	var bIsUc7 = sUserAgent.match(/rv:1.2.3.4/i) == "rv:1.2.3.4";
	var bIsUc = sUserAgent.match(/ucweb/i) == "ucweb";
	var bIsAndroid = sUserAgent.match(/android/i) == "android";
	var bIsCE = sUserAgent.match(/windows ce/i) == "windows ce";
	var bIsWM = sUserAgent.match(/windows mobile/i) == "windows mobile";
	if (!(bIsIpad || bIsIphoneOs || bIsMidp || bIsUc7 || bIsUc || bIsAndroid
			|| bIsCE || bIsWM)) {
		loadConfig();
	} else {
		window.location.href = 'wap/index.html';
	}
}

function loadConfig() {
	var time = getNowFormatDate();
	$('#P_Time').val(time);

	var radio = "";
	//1为pc  0为都支持 2为手机
	$.get("/pay/getPayType",function(obj) {
		var flag = 0;
		$.each(obj.data,function(i, item) {
			if (item.pay_model != "2" ) {
				radio = radio
						+ "<label class='pay-label'>"
						+ "<input type='radio' name='bank_code' onclick=\"rechargeLimit();\" model='"+item.pay_model+"' class='regular-radio' value='"
						+ item.item_code + "'/>"
						+ "<img src='win/images/" + item.icon + ".png' class='paytype' /></label>";
				if ((flag + 1) % 3 === 0) {
					radio = radio + "<br/>"
				}
				flag ++;
			}
		});
		$("#redioTd").html(radio);
		if(radio != ""){
			$('input[name="bank_code"]').get(0).checked = true;
			rechargeLimit();
		}
	});
}

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

function showBank() {
	if ($("#radwangyin").attr("checked")) {
		$("#banklist").show();
	}
	$(".regular-radio,.showbank").click(function() {
		var cvl = $("input[name='bank_code']:checked").val();
		if (cvl == "BANK") {
			$("#banklist").show();
		} else {
			$("#banklist").hide();
		}
	});
}



function btnOKonclick() {
	var username = $("#username").val();
	var usern = /^[a-zA-Z0-9]{1,}$/;
	if (!usern.test(username)) {
        layer.alert('会员帐号只能由数字、字母组成!');
		return false;
	}
	var coin = $("#coin").val();
	var bankck = $('input[name="bank_code"]:checked').val();
	var rusername = $("#rusername").val();
	if (username == null || username == "") {
        layer.alert("[提示]用户名不能为空！");
		$("#username").focus();
		return false;
	}
	if (rusername == null || rusername == "" || rusername != username) {
        layer.alert("[提示]2次用户输入不一致！");
		$("#rusername").focus();
		return false;
	}
	if (bankck == null || bankck == "") {
        layer.alert("[提示]支付类型不能为空！");
		return false;
	}
	if (isNaN(coin)) {
        layer.alert("[提示]存款额度非有效数字！");
		$("#coin").focus();
		return false;
	}
	
	if(!isMoney(coin)){
		layer.alert("[提示]存款额度非有效数字！");
		$("#coin").focus();
		return false;
	}
	
	// 判断存款额度是否正常 
	var saveLimit = $('#saveLimit').val().split(",");
	if(parseFloat(coin)<parseFloat(saveLimit[0])||parseFloat(coin)>parseFloat(saveLimit[1])){
		layer.alert("[提示]存款额度在"+saveLimit[0]+"~"+saveLimit[1]);
		$("#coin").focus();
		// return false;
	}

	// if (coin < 10) {
	// layer.alert("[提示]10元以上才能存款！");
	// $("#coin").focus();
	// return false;
	//	}
	
	//	if (coin > 50000) {
	//        layer.alert("[提示]存款金额不能超过50000！");
	//		$("#coin").focus();
	//	}
	var createTime = $('#P_Time').val();
	var paramO = {
		backcode : bankck,
		username : username,
		amount : coin,
		applyDate : createTime,
		userIp : returnCitySN["cip"],
	}
//	$("#loadingDiv").show();
//	$.ajax({
//		url : '/pay/server',
//		dataType : 'json',
//		data : JSON.stringify(data),
//		contentType : "application/json",
//		cache : false,
//		type : 'POST',
//		success : function(obj) {
//			if (obj.code == 200) {
//				postcall(obj.data);
//				$("#loadingDiv").hide();
//			} else {
//				alert(obj.message);
//				$("#loadingDiv").hide();
//			}
//		},
//		error : function(XMLHttpRequest, textStatus, errorThrown) {
//			$("#loadingDiv").hide();
//		}
//	})
    var model=$('input[name="bank_code"]:checked').attr("model");
	if(model=="3"||model=='4'){
        $.ajax({
            url: "/pay/getModeType?itemCode=CYBER_BANK&username=" + paramO.username,
            type: "get",
            async: false,
            contentType: 'application/json',
            success: function (data) {
                if (data == "3") {
                    paramO.model = data;
                    window.location.href = "bank.html?param=" + encodeURIComponent(JSON.stringify(paramO));
                    return;
                }
            }
        });
    }
    if( paramO.model!="3"){
        var dataP = {
            url:"/pay/server",
            param:paramO
        }
        postcall(dataP);
    }

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

/**
 * 支付类型限额展示
 */
function rechargeLimit() {

	var payWay = $("input[name='bank_code']:checked").val();

	$.get("/pay/getPayTypeLimit", {payType : payWay}, function(obj) {
		//$("#coin").attr("placeholder", obj);
    	$('#saveLimit').val(obj);
    	var limitNumbers = obj.split(",");
        $('#coin').attr("placeholder","存款额度在"+limitNumbers[0]+"~"+limitNumbers[1]);
		
	});

}

/**
 * 加载首页的温馨提示 
 */
function loadNotify() {
    $.get("/pay/getValueByKey/index_notify", {}, function (obj) {
        $('#notify').text(obj);
    });
}


