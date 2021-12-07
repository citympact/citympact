
$(document).ready(function() {
    let modal = new bootstrap.Modal(document.getElementById("popup"));
    var prepareModal = function(response) {

        $("#popup_title").html(response.popup_title);
        $("#popup_content").html(response.popup_content);
        $("#popup_next_button").html(response.popup_next_button_val);
        if(response.popup_next_button_val == null ||
            response.popup_next_button_val.length < 1
        ) {
            $("#popup_next_button").hide();
        } else {
            $("#popup_next_button").show().addClass('disabled');
        }

        popupFormAudited = false;
        $("#popup_content").find("input").each(function(i, e) {
            console.log("item =", i, e)
        });

    };
    $("a.upvote,a.downvote").click(function(event) {
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
            prepareModal(response);
            modal.show();


        });
        event.preventDefault();
    });

    $("#popup_next_button").click(function() {
        popupForm = $("#popup").find("form").eq(0);
        data = popupForm.serializeArray();
        data.push({
            name: "csrfmiddlewaretoken",
            value: $("#vote_csrf_token").val()
        });

        $.post(popupForm.attr('action'), data, function(response) {
            prepareModal(response);
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
                    newLi.click(function(event) {
                        console.log("click..")
                        if(suggestionsDiv !== undefined) {
                            suggestionsDiv.hide();
                        }
                        window.location.href = newLi.find("a").attr("href");
                        event.preventDefault();
                        return false;
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
                    updatedSelection = false;
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
                            updatedSelection = true;
                        break;

                        case 39: // right
                        break;

                        case 40: // down
                            selectedIndex++;
                            updatedSelection = true;
                        break;

                        default: return; // exit this handler for other keys
                    }
                    let maxSel = response.suggestions.length + 1;
                    selectedIndex = (selectedIndex +maxSel) % maxSel
                    suggestionsUl.children().removeClass("active-suggestion");
                    suggestionsUl.children().eq(selectedIndex).addClass("active-suggestion")
                    if(updatedSelection) {
                        e.preventDefault(); // prevent the default action
                        return false;
                    }
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

    $("a.sign_petition").click(function(event) {
        let clickedElement = $(this);
        let petition_id = $(this).parents("div").first().data("petition-id");

        $.get("petition/sign",  {
            petition_id: petition_id,
            csrfmiddlewaretoken: $("#vote_csrf_token").val(),
        },
        function(response) {
            if(response.result == "redirect") {
                window.location.href = response.url;
            } else if(response.result == "OK") {
                prepareModal(response);
                modal.show();
            }
        });
        event.preventDefault();
    });
});
