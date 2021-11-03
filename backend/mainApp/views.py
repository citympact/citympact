from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from .models import *


def index(request):
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


class ProjectListView(generic.ListView):
    context_object_name = "last_projects"
    template_name = "mainApp/index.html"

    def get_queryset(self):
        return CityProject.objects.all()

class VoteProject(generic.View):
    def post(self, request):
        if "project_id" in request.POST and "vote" in request.POST:
            project_id = int(request.POST["project_id"])
            vote = int(request.POST["vote"])
            if not "voted_projects" in request.session:
                request.session["voted_projects"] = []
            if not project_id in request.session["voted_projects"]:
                project = CityProject.objects.get(pk=project_id)
                vote = CityProjectVote(project=project, vote=vote)
                vote.save()
                request.session["voted_projects"].append(project_id)
        return JsonResponse({
            "result": "OK",
            "project_id":project_id,
            "vote":vote});
