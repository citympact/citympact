
$(document).ready(function() {
    $("a.upvote,a.downvote").click(function() {
        let project_id = $(this).parents("div.project-div").first().data("project-id");
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
    $("a.vote-star").click(function() {
        let clickedElement = $(this);
        let petition_id = $(this).parents("div").first().data("petition-id");
        let vote = 5-$(this).data("vote-val");
        $.post("petition/vote",  {
            petition_id: petition_id,
            vote: vote,
            csrfmiddlewaretoken: $("#vote_csrf_token").val(),
        },
        function(response) {
            clickedElement.parent().children().each(function(i, e) {
                if(5-i<=response.vote) {
                    $(e).addClass("star-activated")
                } else {
                    $(e).removeClass("star-activated")
                }
            });
        });
    });
});
