function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {
    $(".pass_info").submit(function (e) {
        e.preventDefault();

        // TODO 修改密码
        // old_password = $('#old_password').val();
        // new_password = $('#new_password').val();
        // new_password2 = $('#new_password2').val();
        // if (new_password != new_password2){
        //     alert('密码不一致')
        // }
        $(this).ajaxSubmit({
            url: "/user/pass_info",
            type: "post",
            // contentType: "application/json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
             success: function (response) {
                if (response.errno == 200) {
                    // 修改成功
                    alert("修改成功");
                    window.location.reload()
                }else {
                    alert(response.errmsg)
                }
            }
        })
    })
});