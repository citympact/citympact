$(document).ready(function() {
    let postValidation = function(type, item_id, action, div) {
        $.post("/manager/",  {
            type: type,
            item_id: item_id,
            action: action,
            csrfmiddlewaretoken: $("#vote_csrf_token").val(),
        },
        function(response){
            if(response.status=="ok") {
                div.html(response.text).delay(400 ).fadeOut(400);
            }
        });
    }
    $(".manage_comment").click(function() {
        let type = $(this).data("type");
        let item_id = $(this).data("comment-id");
        let action = $(this).data("action");
        let comment_div = $(this).parents(".manage_group_div").first();
        postValidation(type, item_id, action, comment_div);
        event.preventDefault();
    });
        $(".manage_proposition").click(function() {
        let type = "Proposition";
            let item_id = $(this).data("proposition-id");
            let action = $(this).data("action");
            let proposition_div = $(this).parents(".manage_group_div").first();
            postValidation(type, item_id, action, proposition_div);
            event.preventDefault();
        });
});
