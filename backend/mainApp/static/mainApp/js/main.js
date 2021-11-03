
$(document).ready(function() {
    $("a.upvote, a.downvote").click(function() {
        let project_id = $(this).parents("div").first().find("input[name=project_id]").val();
        let vote = 1;
        if($(this).hasClass("downvote")) {
            vote = -1;
        }
        $.post("project/vote",  {
            project_id: project_id,
            vote: vote,
            csrfmiddlewaretoken: $("#vote_csrf_token").val(),
        },
        function(response){
            console.log("response = ", response)
        });
    });
});
