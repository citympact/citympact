from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib.sessions.backends.db import SessionStore
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.db.utils import IntegrityError
from django.db.models import Q
from .models import *
from .forms import *

import urllib.parse

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words


LANGUAGE = "french"
SUMMARY_SENTENCES_COUNT = 3
MESSAGE_SEVERITIES = ["primary", "secondary", "success", "danger", "warning",
    "info", "light", "dark"]




class IndexView(generic.View):
    def get(self, request, *args, **kwargs):

        print("user =", request.user)

        visitor = Visitor.objects.get(pk=request.session["visitor_id"])

        projects = CityProject.objects.all();
        # Fetching the vote (integers) of the user for each project:
        votes = [ \
            ["", ""] if (v is None or v.vote==0) \
            else \
                ["", "active-vote"] if v.vote>0 else ["active-vote",""] \
            for v in
                [p.cityprojectvote_set.all().filter(visitor=visitor).first() \
                    for p in projects\
                ] \
        ]
        petitions = Petition.objects.all();

        # Retrieving the last message, if any, and resetting since it will be
        # displayed by the HTML template:
        message = None
        if "message" in request.session:
            message = {
                "content": request.session["message"],
                "severity": MESSAGE_SEVERITIES[0]
            }

            if "severity" in request.session:
                if request.session["severity"] in MESSAGE_SEVERITIES:
                    message["severity"] = request.session["severity"]
                del request.session["severity"]

            del request.session["message"]

        context = {
            'projects_votes': list(zip(projects, votes)),
            "petitions": petitions,
            "star_range": list(range(5)),
            "message" : message,
        }
        return render(request, 'mainApp/index.html', context)

def _contextifyDetail(databaseObject):
    return {
            "title": databaseObject.title,
            "description": databaseObject.description,
            "image": databaseObject.image,
        }
class AccountsProfile(generic.View):
    def get(self, request, *args, **kwargs):
        user_form = UserForm(instance=request.user)

        # Quickly making sure that the associated registered user exists:
        RegisteredUser.objects.get_or_create(user=request.user)

        registered_user_form = \
            RegisteredUserForm(instance=request.user.registereduser)
        context = {
            'user_form': user_form,
            'registered_user_form': registered_user_form
        }
        return render(request, 'mainApp/account_profile.html', context)

    def post(self, request, *args, **kwargs):
        user_form = UserForm(request.POST, request.FILES, instance=request.user)


        registered_user_form = RegisteredUserForm(request.POST, request.FILES, instance=request.user.registereduser)

        if user_form.is_valid():
            user_form.save()
        if registered_user_form.is_valid():
            registered_user_form.save()

        return HttpResponseRedirect(reverse('mainApp:accounts_profile', args=()))

class ProjectView(generic.View):
    def get(self, request, *args, **kwargs):
        context = \
            _contextifyDetail(CityProject.objects.get(pk=kwargs["project_id"]))
        return render(request, 'mainApp/detailView.html', context)

class PetitionView(generic.View):
    def get(self, request, *args, **kwargs):

        context = \
            _contextifyDetail(Petition.objects.get(pk=kwargs["petition_id"]))
        return render(request, 'mainApp/detailView.html', context)

class AddNewPetition(generic.View):
    def post(self, request, *args, **kwargs):
        session = Session.objects.get(pk=request.session.session_key)
        if "title" in request.POST and \
            "description" in request.POST and \
            "image" in request.FILES and \
            session is not None:

            # Computing the summary:
            parser = PlaintextParser.from_string(request.POST["description"],
                Tokenizer(LANGUAGE))
            stemmer = Stemmer(LANGUAGE)
            summarizer = LsaSummarizer(stemmer)
            summarizer.stop_words = get_stop_words(LANGUAGE)
            summary = " ".join([str(x) for x in summarizer(parser.document,
                SUMMARY_SENTENCES_COUNT)])

            petition = Petition(title=request.POST["title"],
                description=request.POST["description"],
                summary=summary,
                session=session,
                image=request.FILES["image"]
            )
            petition.save()
            request.session["message"] = "Nouvelle pétition ajoutée."
        else:
            request.session["message"] = "Impossible d'enregistrer votre petition."
            request.session["severity"] = "danger"

        return HttpResponseRedirect(reverse('mainApp:index', args=()))

    def get(self, request, *args, **kwargs):
        title = ""
        if "title" in request.GET:
            title = request.GET["title"]
        return render(request, "mainApp/newPetition.html", {
            "title": title
        })

class SearchView(generic.View):
    def post(self, request, *args, **kwargs):
        """
        This function searches the petitions and projects given a provided text
        input from the search bar.
        """

        if not "content" in request.POST:
            return JsonResponse({"result": "refused"});

        suggestions = []

        petitions = Petition.objects.filter(Q(title__icontains=request.POST["content"]))
        suggestions += [{"url": reverse('mainApp:petitionDetail', kwargs={'petition_id': p.id}), "title": """<span class="badge bg-success rounded-pill">Petition</span> """+p.title} for p in petitions]


        cityProjects = CityProject.objects.filter(Q(title__icontains=request.POST["content"]))
        suggestions += [{"url": reverse('mainApp:projectDetail', kwargs={'project_id': p.id}), "title": """<span class="badge bg-info rounded-pill">Projet</span> """+p.title} for p in cityProjects]

        # Sorting and keeping at max 5 items:
        suggestions = sorted(suggestions, key=lambda x: x["title"])[:min(len(suggestions),5)]

        return JsonResponse({
            "result": "ok",
            "suggestions": suggestions
            });


def create_sharing_div(target_url, link_title):
    link_title = urllib.parse.quote(link_title)
    sharePlatforms = {
        """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-facebook" viewBox="0 0 16 16">
<path d="M16 8.049c0-4.446-3.582-8.05-8-8.05C3.58 0-.002 3.603-.002 8.05c0 4.017 2.926 7.347 6.75 7.951v-5.625h-2.03V8.05H6.75V6.275c0-2.017 1.195-3.131 3.022-3.131.876 0 1.791.157 1.791.157v1.98h-1.009c-.993 0-1.303.621-1.303 1.258v1.51h2.218l-.354 2.326H9.25V16c3.824-.604 6.75-3.934 6.75-7.951z"/>
</svg>""": "https://www.facebook.com/sharer/sharer.php?u=" + target_url,

        """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-twitter" viewBox="0 0 16 16">
<path d="M5.026 15c6.038 0 9.341-5.003 9.341-9.334 0-.14 0-.282-.006-.422A6.685 6.685 0 0 0 16 3.542a6.658 6.658 0 0 1-1.889.518 3.301 3.301 0 0 0 1.447-1.817 6.533 6.533 0 0 1-2.087.793A3.286 3.286 0 0 0 7.875 6.03a9.325 9.325 0 0 1-6.767-3.429 3.289 3.289 0 0 0 1.018 4.382A3.323 3.323 0 0 1 .64 6.575v.045a3.288 3.288 0 0 0 2.632 3.218 3.203 3.203 0 0 1-.865.115 3.23 3.23 0 0 1-.614-.057 3.283 3.283 0 0 0 3.067 2.277A6.588 6.588 0 0 1 .78 13.58a6.32 6.32 0 0 1-.78-.045A9.344 9.344 0 0 0 5.026 15z"/>
</svg>""": "https://twitter.com/intent/tweet?text=%s %s" \
        % (link_title, target_url),

        """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-reddit" viewBox="0 0 16 16">
<path d="M6.167 8a.831.831 0 0 0-.83.83c0 .459.372.84.83.831a.831.831 0 0 0 0-1.661zm1.843 3.647c.315 0 1.403-.038 1.976-.611a.232.232 0 0 0 0-.306.213.213 0 0 0-.306 0c-.353.363-1.126.487-1.67.487-.545 0-1.308-.124-1.671-.487a.213.213 0 0 0-.306 0 .213.213 0 0 0 0 .306c.564.563 1.652.61 1.977.61zm.992-2.807c0 .458.373.83.831.83.458 0 .83-.381.83-.83a.831.831 0 0 0-1.66 0z"/>
<path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.828-1.165c-.315 0-.602.124-.812.325-.801-.573-1.9-.945-3.121-.993l.534-2.501 1.738.372a.83.83 0 1 0 .83-.869.83.83 0 0 0-.744.468l-1.938-.41a.203.203 0 0 0-.153.028.186.186 0 0 0-.086.134l-.592 2.788c-1.24.038-2.358.41-3.17.992-.21-.2-.496-.324-.81-.324a1.163 1.163 0 0 0-.478 2.224c-.02.115-.029.23-.029.353 0 1.795 2.091 3.256 4.669 3.256 2.577 0 4.668-1.451 4.668-3.256 0-.114-.01-.238-.029-.353.401-.181.688-.592.688-1.069 0-.65-.525-1.165-1.165-1.165z"/>
</svg>""" : "https://www.reddit.com/submit?title=%s&url=%s" % (link_title, target_url),

        """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-whatsapp" viewBox="0 0 16 16">
<path d="M13.601 2.326A7.854 7.854 0 0 0 7.994 0C3.627 0 .068 3.558.064 7.926c0 1.399.366 2.76 1.057 3.965L0 16l4.204-1.102a7.933 7.933 0 0 0 3.79.965h.004c4.368 0 7.926-3.558 7.93-7.93A7.898 7.898 0 0 0 13.6 2.326zM7.994 14.521a6.573 6.573 0 0 1-3.356-.92l-.24-.144-2.494.654.666-2.433-.156-.251a6.56 6.56 0 0 1-1.007-3.505c0-3.626 2.957-6.584 6.591-6.584a6.56 6.56 0 0 1 4.66 1.931 6.557 6.557 0 0 1 1.928 4.66c-.004 3.639-2.961 6.592-6.592 6.592zm3.615-4.934c-.197-.099-1.17-.578-1.353-.646-.182-.065-.315-.099-.445.099-.133.197-.513.646-.627.775-.114.133-.232.148-.43.05-.197-.1-.836-.308-1.592-.985-.59-.525-.985-1.175-1.103-1.372-.114-.198-.011-.304.088-.403.087-.088.197-.232.296-.346.1-.114.133-.198.198-.33.065-.134.034-.248-.015-.347-.05-.099-.445-1.076-.612-1.47-.16-.389-.323-.335-.445-.34-.114-.007-.247-.007-.38-.007a.729.729 0 0 0-.529.247c-.182.198-.691.677-.691 1.654 0 .977.71 1.916.81 2.049.098.133 1.394 2.132 3.383 2.992.47.205.84.326 1.129.418.475.152.904.129 1.246.08.38-.058 1.171-.48 1.338-.943.164-.464.164-.86.114-.943-.049-.084-.182-.133-.38-.232z"/>
</svg>""": "https://api.whatsapp.com/send?text=%s %s" \
            % (link_title, target_url),
        """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-telegram" viewBox="0 0 16 16">
<path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM8.287 5.906c-.778.324-2.334.994-4.666 2.01-.378.15-.577.298-.595.442-.03.243.275.339.69.47l.175.055c.408.133.958.288 1.243.294.26.006.549-.1.868-.32 2.179-1.471 3.304-2.214 3.374-2.23.05-.012.12-.026.166.016.047.041.042.12.037.141-.03.129-1.227 1.241-1.846 1.817-.193.18-.33.307-.358.336a8.154 8.154 0 0 1-.188.186c-.38.366-.664.64.015 1.088.327.216.589.393.85.571.284.194.568.387.936.629.093.06.183.125.27.187.331.236.63.448.997.414.214-.02.435-.22.547-.82.265-1.417.786-4.486.906-5.751a1.426 1.426 0 0 0-.013-.315.337.337 0 0 0-.114-.217.526.526 0 0 0-.31-.093c-.3.005-.763.166-2.984 1.09z"/>
</svg>""": "https://t.me/share/url?text=%s&url=%s" % (link_title, target_url),
        """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-linkedin" viewBox="0 0 16 16">
<path d="M0 1.146C0 .513.526 0 1.175 0h13.65C15.474 0 16 .513 16 1.146v13.708c0 .633-.526 1.146-1.175 1.146H1.175C.526 16 0 15.487 0 14.854V1.146zm4.943 12.248V6.169H2.542v7.225h2.401zm-1.2-8.212c.837 0 1.358-.554 1.358-1.248-.015-.709-.52-1.248-1.342-1.248-.822 0-1.359.54-1.359 1.248 0 .694.521 1.248 1.327 1.248h.016zm4.908 8.212V9.359c0-.216.016-.432.08-.586.173-.431.568-.878 1.232-.878.869 0 1.216.662 1.216 1.634v3.865h2.401V9.25c0-2.22-1.184-3.252-2.764-3.252-1.274 0-1.845.7-2.165 1.193v.025h-.016a5.54 5.54 0 0 1 .016-.025V6.169h-2.4c.03.678 0 7.225 0 7.225h2.4z"/>
</svg>""": "https://www.linkedin.com/sharing/share-offsite/?url=%s"% ( target_url),
    }

    shareButtons = "";
    for name, link in sharePlatforms.items():
        shareButtons += "<a href=\"%s\" target=\"_blank\">%s</a> " \
            % (link, name)
    return "<div><h4>Partager ce projet:</h4>" \
        + """<p class="pb-5">""" + shareButtons + """</p></div>"""

class AddVoteComment(generic.View):
    def _create_stats_div(self, project_id):
        project = CityProject.objects.get(pk=project_id)
        up_votes = len(
            [v.vote for v in project.cityprojectvote_set.all().filter(vote=1)])
        down_votes = len(
            [v.vote for v in project.cityprojectvote_set.all().filter(vote=-1)])

        return "<div><h4>Vote actuel:</h4>" \
            + """<p class="pb-5">%d positifs, %d négatifs.</p></div>""" \
            % (up_votes, down_votes)


    def post(self, request, *args, **kwargs):
        visitor = Visitor.objects.get(pk=request.session["visitor_id"])
        if visitor == None or \
            not "project_id" in request.POST or \
            not "comment" in request.POST \
        :
            return JsonResponse({"result": "refused"});

        vote = CityProjectVote.objects.get(
            project=request.POST["project_id"],
            visitor=visitor
        )
        vote.comment = request.POST["comment"]
        vote.save()

        project = CityProject.objects.get(pk=request.POST["project_id"])
        up_votes = len(
            [v.vote for v in project.cityprojectvote_set.all().filter(vote=1)])
        down_votes = len(
            [v.vote for v in project.cityprojectvote_set.all().filter(vote=-1)])

        project_url = "%s://%s" \
            % (request.scheme, request.META["HTTP_HOST"]) \
            + reverse('mainApp:projectDetail', kwargs={
                'project_id': project.id
            })

        additional_div = ""
        if vote.vote < 0:
            petition_title = urllib.parse.quote(
                "Pétition contre le projet "+project.title)
            additional_div = """<div><h4>Créer une pétition:</h4>""" \
                + """<p class="pb-5">Vous n'avez pas aimé ce projet, voulez-vous <a href="%s?title=%s">créer une pétition</a>?</p></div>""" \
                % (
                    reverse('mainApp:addNewPetition', args=()),
                    petition_title
                )

        return JsonResponse({
            "result": "ok",
            "popup_title": "Merci pour votre vote!",
            "popup_content":
                self._create_stats_div(request.POST["project_id"]) \
                + create_sharing_div(project_url, project.title) \
                + additional_div,
            "popup_next_button_val": None
        })

class VoteProject(generic.View):

    def _create_followup_form(self, project_id, project_name, vote):
        if vote > 0:
            title = "Je trouve le projet %s très bien car:" % project_name
        else:
            title = "Je n'aime pas le projet %s car:" % project_name

        return """
            <h5>""" + title + """</h5>
            <form action="%s">
            <textarea name="comment"></textarea>
            <input type="hidden" name="project_id" value="%d" />
            <input type="hidden" name="vote" value="%d" />
            </form>
        """ % (reverse('mainApp:addVoteComment', args=()), project_id, vote)

    def post(self, request, *args, **kwargs):
        """
        Posting a vote should be unique per user. Hence session are used here to
        store a dict of previously voted project ids. This is a quick solution
        as long as no better user handling is implemented.
        Todo: register each vote with user id.
        """

        visitor = Visitor.objects.get(pk=request.session["visitor_id"])
        if visitor == None or \
            not "project_id" in request.POST or \
            not "vote" in request.POST\
        :
            return JsonResponse({"result": "refused"});


        project_id = int(request.POST["project_id"])
        vote = int(request.POST["vote"])
        project = CityProject.objects.get(pk=project_id)
        vote_object, new_vote = CityProjectVote.objects.get_or_create(
            project=project,
            visitor=visitor
        )
        vote_object.vote = vote
        vote_object.save()

        popup_content = self._create_followup_form(project.id, project.title, vote)

        return JsonResponse({
            "result": "OK",
            "new_vote": new_vote,
            "vote":vote_object.vote,
            "popup_title": "Merci pour votre vote",
            "popup_content": popup_content,
            "popup_next_button_val": "Commenter",
        });


class SignPetition(generic.View):
    def post(self, request, *args, **kwargs):
        """
        Post a new signature (from the confirmation popup).
        """

        session = Session.objects.get(pk=request.session.session_key)
        if session == None or \
            not "petition_id" in request.POST \
        :
            return JsonResponse({"result": "refused"});

        petition_id = int(request.POST["petition_id"])
        petition = Petition.objects.get(pk=petition_id)

        signature, is_new_signature = PetitionSignature.objects.get_or_create(
            petition=petition,
            session=session
        )
        signature.save()

        petition_url = "%s://%s" \
            % (request.scheme, request.META["HTTP_HOST"]) \
            + reverse('mainApp:petitionDetail', kwargs={
                'petition_id': petition.id
            })

        popup_content = """<h4>Merci</h4>""" \
            + """<p class="pb-5"> Merci pour votre signature</p>""" \
            + create_sharing_div(petition_url, petition.title)
        return JsonResponse({
            "result": "OK",
            "popup_title": "Pétition signée",
            "popup_content": popup_content,
            "popup_next_button_val": None
            });

    def get(self, request, *args, **kwargs):
        """
        Return the popup content of a signature confirmation
        """

        session = Session.objects.get(pk=request.session.session_key)
        if session == None or \
            not "petition_id" in request.GET \
        :
            return JsonResponse({"result": "refused"});

        petition_id = int(request.GET["petition_id"])
        petition = Petition.objects.get(pk=petition_id)
        popup_content = "<p>Êtes-vous sûr de signer la pétition intitulée :" \
            + "<br><em>%s</em></p>" % petition.title \
            + """<form action="%s">
                <input type="hidden" name="petition_id" value="%d" />
                </form>
                """ % (reverse('mainApp:signPetition', args=()), petition_id)
        return JsonResponse({
            "result": "OK",
            "popup_title": "Confirmation de signature",
            "popup_content": popup_content,
            "popup_next_button_val": "Signer la pétition"
            });
