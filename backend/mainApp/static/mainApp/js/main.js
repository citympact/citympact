
$(document).ready(function() {
    $("a.upvote,a.downvote").click(function() {
        let project_id = $(this).parents("div").first().data("project-id");
        let vote = $(this).hasClass("upvote") ? 1  : -1;
        if($(this).hasClass("active-vote")) {
            vote = 0;
        }
        let clickedElement = $(this);
        clickedElement.parent().find("a.upvote,a.downvote").removeClass("active-vote");
        $.post("project/vote",  {
            project_id: project_id,
            vote: vote,
            csrfmiddlewaretoken: $("#vote_csrf_token").val(),
        },
        function(response){
            if(response.vote!=0) {
                clickedElement.addClass("active-vote");
            }

        });
    });
});
