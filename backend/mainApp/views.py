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

    context = {
        'last_projects': CityProject.objects.all(),
    }
    return render(request, 'mainApp/index.html', context)

def detail(request, project_id):
    return HttpResponse("Detail of project id = %d" % project_id)

def addNewProject(request):
    if("title" in request.POST and "description" in request.POST):
        c = CityProject(title=request.POST["title"],
            description=request.POST["description"])
        c.save()
        return HttpResponseRedirect(reverse('mainApp:addNewProject', args=()))
    return render(request, "mainApp/new.html", {})


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
        not "vote" in request.POST:
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
