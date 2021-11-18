from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib.sessions.backends.db import SessionStore
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.db.utils import IntegrityError
from django.db.models import Q
from .models import *

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words


LANGUAGE = "french"
SUMMARY_SENTENCES_COUNT = 3
MESSAGE_SEVERITIES = ["primary", "secondary", "success", "danger", "warning",
    "info", "light", "dark"]

def index(request):
    # FixMe: implement a propper user login feature and not only a session id
    # based "authentication".
    if not request.session.session_key:
        request.session.save()
    session = Session.objects.get(pk=request.session.session_key)

    projects = CityProject.objects.all();
    # Fetching the vote (integers) of the user for each project:
    votes = [ \
        ["", ""] if (v is None or v.vote==0) \
        else \
            ["", "active-vote"] if v.vote>0 else ["active-vote",""] \
        for v in
            [p.cityprojectvote_set.all().filter(session=session).first() \
                for p in projects\
            ] \
    ]
    petitions = Petition.objects.all();


    star_range_and_class = [
         list(enumerate([""]*5)) if p is None else list(enumerate(["" for x in range(p.vote, 5)]+["star-activated" for x in range(p.vote)])) for p in
         [p.petitionvote_set.all().filter(session=session).first() \
            for p in petitions\
        ]
    ]

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
def projectDetail(request, project_id):
    context = _contextifyDetail(CityProject.objects.get(pk=project_id))
    return render(request, 'mainApp/detailView.html', context)

def petitionDetail(request, petition_id):
    context = _contextifyDetail(Petition.objects.get(pk=petition_id))
    return render(request, 'mainApp/detailView.html', context)

class AddNewPetition(generic.View):
    def post(self, request):
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
            print("request.POST =", request.POST)
            print("request.FILES =", request.FILES)
            request.session["message"] = "Impossible d'enregistrer votre petition."
            request.session["severity"] = "danger"

        return HttpResponseRedirect(reverse('mainApp:index', args=()))

    def get(self, request):
        return render(request, "mainApp/newPetition.html", {})

class SearchView(generic.View):
    def post(self, request):
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

class VoteProject(generic.View):

    def _create_followup_form(self, project_name, vote):
        if vote > 0:
            title = "Je trouve le projet %s très bien car:" % project_name
        else:
            title = "Je n'aime pas le projet %s car:" % project_name

        return """
            <h5>""" + title + """</h5>
            <textarea></textarea>
        """
    def post(self, request):
        """
        Posting a vote should be unique per user. Hence session are used here to
        store a dict of previously voted project ids. This is a quick solution
        as long as no better user handling is implemented.
        Todo: register each vote with user id.
        """
        session = Session.objects.get(pk=request.session.session_key)
        if session == None or \
            not "project_id" in request.POST or \
            not "vote" in request.POST\
        :
            return JsonResponse({"result": "refused"});


        project_id = int(request.POST["project_id"])
        vote = int(request.POST["vote"])
        project = CityProject.objects.get(pk=project_id)
        vote_object, new_vote = CityProjectVote.objects.get_or_create(
            project=project,
            session=session
        )
        vote_object.vote = vote
        vote_object.save()

        up_votes = len(
            [v.vote for v in project.cityprojectvote_set.all().filter(vote=-1)])
        down_votes = len(
            [v.vote for v in project.cityprojectvote_set.all().filter(vote=1)])

        popup_content = "<h4>Vote actuel:</h4>" \
            + """<p class="pb-5">%d positifs, %d négatifs.</p>""" \
            % (up_votes, down_votes) \
            + self._create_followup_form(project.title, vote)

        return JsonResponse({
            "result": "OK",
            "project_id":project_id,
            "new_vote": new_vote,
            "vote":vote_object.vote,
            "popup_title": "Merci pour votre vote",
            "popup_content": popup_content,
            "popup_next_button_val": "Commenter"});

class VotePetition(generic.View):
    def post(self, request):
        """
        Posting a 5-star based vote for a given petition
        (read the comment of the class above for more details)
        """
        session = Session.objects.get(pk=request.session.session_key)
        if session == None or \
            not "petition_id" in request.POST or \
            not "vote" in request.POST\
        :
            return JsonResponse({"result": "refused"});


        petition_id = int(request.POST["petition_id"])
        vote = int(request.POST["vote"])

        petition = Petition.objects.get(pk=petition_id)
        vote_object, new_vote = PetitionVote.objects.get_or_create(
            petition=petition,
            session=session
        )
        vote_object.vote = vote
        vote_object.save()

        return JsonResponse({
            "result": "OK",
            "petition_id":petition_id,
            "new_vote": new_vote,
            "vote":vote_object.vote});
