from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib.sessions.backends.db import SessionStore
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.db.utils import IntegrityError
from .models import *


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


    print([x for x in [p.petitionvote_set.all().filter(session=session).first() for p in petitions] if x is not None])

    star_range_and_class = [
         list(enumerate([""]*5)) if p is None else list(enumerate(["" for x in range(p.vote, 5)]+["star-activated" for x in range(p.vote)])) for p in
         [p.petitionvote_set.all().filter(session=session).first() \
            for p in petitions\
        ]
    ]
    print("v=", list(zip(petitions, star_range_and_class)))

    context = {
        'projects_votes': list(zip(projects, votes)),
        "petitions": list(zip(petitions, star_range_and_class)),
        "star_range": list(range(5))
    }
    return render(request, 'mainApp/index.html', context)

def detail(request, project_id):
    return HttpResponse("Detail of project id = %d" % project_id)

def addNewPetition(request):
    if("title" in request.POST and "description" in request.POST):
        c = CityProject(title=request.POST["title"],
            description=request.POST["description"])
        c.save()
        return HttpResponseRedirect(reverse('mainApp:addNewPetition', args=()))
    return render(request, "mainApp/newPetition.html", {})


class VoteProject(generic.View):
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

        return JsonResponse({
            "result": "OK",
            "project_id":project_id,
            "new_vote": new_vote,
            "vote":vote_object.vote});

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
