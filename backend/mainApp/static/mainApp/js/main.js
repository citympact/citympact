
$(document).ready(function() {
    $("a.upvote,a.downvote").click(function() {
        let project_id = $(this).parents("div.project-div")
            .first().data("project-id");
        let vote = $(this).hasClass("upvote") ? 1  : -1;
        if($(this).hasClass("active-vote")) {
            vote = 0;
        }
        let clickedElement = $(this);
        clickedElement.parent().find("a.upvote,a.downvote")
            .removeClass("active-vote");
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

    let suggestionsDiv;
    var selectedIndex = -1;
    $("#search-input").on('input', function() {
        let inputElement = $(this);
        suggestionsDiv = $(this).parent().find(".suggestions-dropdown").first();
        let suggestionsUl = suggestionsDiv.find("ul")

        suggestionsDiv.show();
        $.post("search",  {
            content: $(this).val(),
            csrfmiddlewaretoken: $("#vote_csrf_token").val(),
        },
        function(response){
            if(response.result == "ok") {
                lastItem = suggestionsUl.children().last();
                // Saving the last link (i.e. the add a new petition link):
                suggestionsUl.empty();
                selectedIndex = -1;
                $.each(response.suggestions, function(i, elt) {
                    let newLi = suggestionsUl
                        .append("<li><a href=\"" + elt.url + "\">" + elt.title
                            + "</a></li>"
                    );
                    // Closing the suggestion div when the user has chosen an
                    // option (i.e. clicked on a proposal):
                    newLi.click(function() {
                        if(suggestionsDiv !== undefined) {
                            suggestionsDiv.hide();
                        }
                    });
                });
                suggestionsUl.append(lastItem);

                // Updating the selected index for the arrow selection to
                // start from this offset:
                $.each(suggestionsUl, function (i, elt) {
                    $(elt).find("a").unbind("hover").hover(function() {
                        suggestionsUl.children()
                            .removeClass("active-suggestion");
                        selectedIndex = suggestionsUl.children().index(
                            $(this).parents("li").first());
                        suggestionsUl.children().eq(selectedIndex).addClass("active-suggestion");
                    });
                });


                inputElement.unbind("keydown").keydown(function(e) {
                    switch(e.which) {
                        case 13: // enter
                            if(selectedIndex>=0) {
                                window.location.href = suggestionsUl.children()
                                    .eq(selectedIndex).find("a").attr("href");
                            }
                        break;
                        case 37: // left
                        break;

                        case 38: // up
                            selectedIndex--;
                        break;

                        case 39: // right
                        break;

                        case 40: // down
                            selectedIndex++;
                        break;

                        default: return; // exit this handler for other keys
                    }
                    let maxSel = response.suggestions.length + 1;
                    selectedIndex = (selectedIndex +maxSel) % maxSel
                    suggestionsUl.children().removeClass("active-suggestion");
                    suggestionsUl.children().eq(selectedIndex).addClass("active-suggestion")
                    e.preventDefault(); // prevent the default action
                    return true;
                });
            }
        });

    });
    $(document).click(function() {
        if(suggestionsDiv !== undefined) {
            suggestionsDiv.hide();
            suggestionsDiv = undefined;
        }
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
