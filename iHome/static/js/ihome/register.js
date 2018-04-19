function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function generateUUID() {
    var d = new Date().getTime();
    if(window.performance && typeof window.performance.now === "function"){
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (d + Math.random()*16)%16 | 0;
        d = Math.floor(d/16);
        return (c=='x' ? r : (r&0x3|0x8)).toString(16);
    });
    return uuid;
}
var imageCodeId = ""
// 生成一个图片验证码的编号，并设置页面中图片验证码img标签的src属性
function generateImageCode() {
    imageCodeId = generateUUID();
    var url = '/api/v1.0/image_code?cur_id=' + imageCodeId;
    $('.image-code>img').attr('src',url)
}

function sendSMSCode() {
    // 校验参数，保证输入框有数据填写
    $(".phonecode-a").removeAttr("onclick");
    var mobile = $("#mobile").val();
    if (!mobile) {
        $("#mobile-err span").html("请填写正确的手机号！");
        $("#mobile-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    } 
    var imageCode = $("#imagecode").val();
    if (!imageCode) {
        $("#image-code-err span").html("请填写验证码！");
        $("#image-code-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    }

    // TODO: 通过ajax方式向后端接口发送请求，让后端发送短信验证码
    var params = {
        'mobile':mobile,
        'image_code':imageCode,
        'image_code_id':imageCodeId
    }
    $.ajax({
        'url':'/api/v1.0/sms_code',
        'type':'post',
        'data':JSON.stringify(params),
        'headers':{
            'X-CSRFToken':getCookie('csrf_token')
        },
        'contentType':'application/json',
        'success':function (res) {
           if (res.errno == '0'){
               var num = 60
               var tid = setInterval(function () {
                   if (num<=0){
                       clearInterval(tid)
                       $('.phonecode-a').text('获取验证码');
                        // 重新添加点击事件
                       $(".phonecode-a").attr("onclick", "sendSMSCode();");
                   }
                   else {
                       $('.phonecode-a').text(num+'秒');
                   }
                   num -= 1

               },1000)

           }
           else {
               $('#phone-code-err span').text(res.errmsg)
               $('#phone-code-err').show
               $(".phonecode-a").attr("onclick", "sendSMSCode();");


           }

        }

    })
}

$(document).ready(function() {
    generateImageCode();  // 生成一个图片验证码的编号，并设置页面中图片验证码img标签的src属性
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#imagecode").focus(function(){
        $("#image-code-err").hide();
    });
    $("#phonecode").focus(function(){
        $("#phone-code-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
        $("#password2-err").hide();
    });
    $("#password2").focus(function(){
        $("#password2-err").hide();
    });

    // TODO: 注册的提交(判断参数是否为空)
    $('.form-register').submit(function (e) {
        e.preventDefault()
        var mobile = $("#mobile").val();
        var phoneCode = $("#phonecode").val();
        var password = $("#password").val();
        var password2 = $("#password2").val();
        if (!mobile) {
            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        }
        if (!phoneCode) {
            $("#phone-code-err span").html("请填写短信验证码！");
            $("#phone-code-err").show();
            return;
        }
        if (!password) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }
        if (password != password2) {
            $("#password2-err span").html("两次密码不一致!");
            $("#password2-err").show();
            return;
        }
        var params = {
            'mobile':mobile,
            'phonecode':phoneCode,
            'password':password
        };
        $.ajax({
            'url':'/api/v1.0/users',
            'type':'post',
            'data':JSON.stringify(params),
            'headers':{
            'X-CSRFToken':getCookie('csrf_token')
            },
            'contentType':'application/json',
            'success':function (req) {
                if (req.errno == '0') {
                    // 注册成功，跳转的首页
                    location.href = 'index.html'
                }
                else {
                    // 注册失败
                    alert(resp.errmsg);
                }

            }
        })



    })
})
