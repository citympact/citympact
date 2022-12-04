$(document).ready(function() {
    $(".manage_comment").click(function() {
        let comment_id = $(this).data("comment-id");
        let type = $(this).data("type");
        let action = $(this).data("action");
        let comment_div = $(this).parents(".manage_group_div").first();

        $.post("/manager/",  {
            comment_id: comment_id,
            type: type,
            action: action,
            csrfmiddlewaretoken: $("#vote_csrf_token").val(),
        },
        function(response){
            if(response.status=="ok") {
                comment_div.html(response.text).delay(400 ).fadeOut(400);
            }
        });
        event.preventDefault();
    });
});
