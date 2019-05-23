function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {

    $(".release_form").submit(function (e) {
        e.preventDefault();

        // TODO 发布完毕之后需要选中我的发布新闻
        // // 选中索引为6的左边单菜单
        // window.parent.fnChangeMenu(6)
        // // 滚动到顶部
        // window.parent.scrollTo(0, 0)
        var input_txt2=$('.input_txt2').val();
        var sel_opt=$('.sel_opt').val();
        var input_multxt=$('.input_multxt').val();
        // var index_image=$('.index_image').val();
        // 使用ajax获取到ckeditor的代码
        var ckeditor = CKEDITOR.instances['ckeditor'].getData()
        var params = {
                // var mobile = $(".login_form #mobile").val();
            'title':input_txt2,
            'category_id':sel_opt,
            'digest':input_multxt,
            // 'index_image':index_image,
            'ckeditor':ckeditor

            };
        $.ajax({
            url:'/user/news_release',
            type:'POST',
            data:JSON.stringify(params),
            contentType:'application/json',
            headers: {'X-CSRFToken': getCookie("csrf_token")},
            success:function (response) {
                if (response.errno==200){
                    alert('ok');
                    location.reload()
                }else{
                    alert(response.errmsg)
                }
            }
        })
        // $(this).ajaxSubmit({
        //     // 读取富文本编辑器里面的文本信息
        //
        //     url: "/user/news_release",
        //     type: "POST",
        //     data:JSON.stringify(params),
        //     headers: {
        //         "X-CSRFToken": getCookie('csrf_token')
        //     },
        //     success: function (resp) {
        //         if (resp.errno == 200) {
        //             // 选中索引为6的左边单菜单
        //             window.parent.fnChangeMenu(6);
        //             // 滚动到顶部
        //             window.parent.scrollTo(0, 0)
        //         }else {
        //             alert(resp.errmsg)
        //         }
        //     }
        // })
    })
});