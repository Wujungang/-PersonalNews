function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {
    $(".pic_info").submit(function (e) {
        e.preventDefault();

        //TODO 上传头像
        $(this).ajaxSubmit({
            url: "/user/pic_info",
            type: "POST",
            headers: {
                "X-CSRFToken": getCookie('csrf_token')
            },
            success: function (response) {
                if (response.errno == 200) {
                    $(".now_user_pic").attr("src", response.data.avatar_url);
                    $(".user_center_pic>img", parent.document).attr("src", response.data.avatar_url);
                    $(".user_login>img", parent.document).attr("src", response.data.avatar_url)
                    location.reload()
                }else {
                    alert(response.errmsg)
                }
            }
        })
    })
})