from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.sessions.backends.db import SessionStore
from django.shortcuts import get_object_or_404, render
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers import serialize
from django.utils.functional import SimpleLazyObject
from django.urls import reverse
from django.views import generic
from django.db.utils import IntegrityError
from django.db.models import Q
from django.db.models import Count
from .models import *
from .forms import *

import urllib.parse
import random
import statistics

"""
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
"""

LANGUAGE = "french"
SUMMARY_SENTENCES_COUNT = 3
MESSAGE_SEVERITIES = ["primary", "secondary", "success", "danger", "warning",
    "info", "light", "dark"]


def render_comment(comment):
    if not comment.validated:
        raise AttributeError(
            "The comment should be validated to be displayed."
        )
    author = "Anne Ho-Nihm";
    if comment.user is not None and comment.name_displayed:
        author = "%s %s" % (comment.user.first_name, comment.user.last_name)

    validated_details = None
    if not comment.name_displayed:
            validated_details = "Commentaire anonyme validé"

    image_ids = [22, 325, 628, 1, 455, 786, 602]
    r = random.randint(0,len(image_ids)-1)
    context = {
        "profile_picture": "https://picsum.photos/id/%d/200/200" % image_ids[r],
        "author_name": author,
        "comment": comment.comment,
        "create_date": comment.create_datetime,
        "validated_details": validated_details,
    }

    return render_to_string("mainApp/comment_detail.html",  context)


class AboutView(generic.View):
    def get(self, request, *args, **kwargs):

        context = {
        }
        return render(request, 'mainApp/about.html', context)

class ContactView(generic.View):
    def get(self, request, *args, **kwargs):

        context = {
        }
        return render(request, 'mainApp/contact.html', context)

class IndexView(generic.View):
    def get(self, request, *args, **kwargs):

        visitor = Visitor.objects.get(pk=request.session["visitor_id"])

        projects = CityProject.objects.all();
        # Fetching the vote (integers) of the user for each project:
        votes = [ \
            ["", ""] if (v is None or v.vote==0) \
            else \
                ["active-vote", ""] if v.vote>0 else ["", "active-vote"] \
            for v in
                [p.cityprojectvote_set.all().filter(visitor=visitor).first() \
                    for p in projects\
                ] \
        ]
        propositions = Proposition.objects.filter(approved=True);

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
            "propositions": propositions,
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

class AccountsCreate(generic.View):
    def get(self, request, *args, **kwargs):

        # Let's see if the account needs to validated:
        if "uid" in kwargs and "token" in kwargs:
            user = User.objects.get(pk=int(kwargs["uid"]))
            if UserTokenGenerator().check_token(user, kwargs["token"]):
                # If the token is valid, then the account is activated:
                user.is_active = True
                user.save()
                messages.add_message(request, messages.INFO, "Compte validé! " \
                    + "Tu peux t'authentifier ci-dessous:")
            return HttpResponseRedirect(reverse('login', args=()))

        new_user_form = NewUserForm()
        context = {
            'new_user_form': new_user_form,
        }
        return render(request, 'mainApp/acccount_create.html', context)

    def post(self, request, *args, **kwargs):
        new_user_form = NewUserForm(request.POST, request.FILES)
        if new_user_form.is_valid():
            new_user_form.set_site_name(request.scheme + "://" + str(get_current_site(request)))
            new_user_form.set_email_sender(settings.DEFAULT_FROM_EMAIL)
            new_user_form.save()

            messages.add_message(request, messages.INFO, 'Compte créé! Un email de confirmation a été envoyé. Merci d\'utiliser le lien dans le mail pour activer votre compte.')
            return HttpResponseRedirect(reverse('mainApp:accounts_profile', args=()))
        else:
            context = {
                'new_user_form': new_user_form,
            }
            return render(request, 'mainApp/acccount_create.html', context)
class AccountsProfile(generic.View):
    def get(self, request, *args, **kwargs):
        user_form = UserForm(instance=request.user)

        # Disabling the edition of the user account fields:
        for name, field in user_form.fields.items():
            field.widget.attrs['readonly'] = True

        # Making sure that the associated registered user exists:
        RegisteredUser.objects.get_or_create(user=request.user)

        registered_user_form = \
            RegisteredUserForm(instance=request.user.registereduser)

        context = {
            'user_form': user_form,
            'registered_user_form': registered_user_form,
        }

        if request.user.registereduser.registration_provider \
        == RegisteredUser.MANUALLY_CREATED:
            context["password_reset"] = True
        else:
            context["registration_provider"] = \
                request.user.registereduser.registration_provider

        return render(request, 'mainApp/account_profile.html', context)

    def post(self, request, *args, **kwargs):
        user_form = UserForm(request.POST, request.FILES, instance=request.user)


        registered_user_form = RegisteredUserForm(request.POST, request.FILES, instance=request.user.registereduser)

        # The user data should not be updated, the fields are set to
        # read-only in the get() function above. For security we never save
        # the form values (e.g. the user could temper the disabled form fields
        # and send a forged HTTP POST request - which is prohibited).
        #if user_form.is_valid():
        #    user_form.save()

        if registered_user_form.is_valid():
            registered_user_form.save()
            messages.add_message(request, messages.INFO, "Compte mis à jour! ")

        return HttpResponseRedirect(reverse('mainApp:accounts_profile', args=()))

class ProjectView(generic.View):
    def get(self, request, *args, **kwargs):
        project = CityProject.objects.get(pk=kwargs["project_id"])

        project.views += 1
        project.save()

        orderedProjects = CityProject.objects.order_by('-views')
        rank = "?"
        for i, p in enumerate(orderedProjects):
            if p == project:
                # zero-starting python index => into human one-starting index:
                rank = i+1
        ranking = "%d / %d" % (rank, len(orderedProjects))


        validated_comments = CityProjectComment.objects.filter(project=project, validated=True).order_by("-create_datetime")

        up_votes = len(
            [v.vote for v in project.cityprojectvote_set.all().filter(vote=1)])
        down_votes = len(
            [v.vote for v in project.cityprojectvote_set.all().filter(vote=-1)])

        context = _contextifyDetail(project)

        rendered_authenticated_comments = []
        rendered_anynymous_comments = []
        for comment in validated_comments:
            if comment.name_displayed:
                rendered_authenticated_comments.append(render_comment(comment))
            else:
                rendered_anynymous_comments.append(render_comment(comment))

        context["authenticated_comments"] = rendered_authenticated_comments
        context["anynymous_comments"] = rendered_anynymous_comments

        context["model_name"] = "project"
        context["id"] = project.id

        context["login_next_url"] = reverse('mainApp:projectDetail', args=(),
            kwargs={'project_id': project.id})
        context["comment_user_name"] = None
        if request.user.is_authenticated:
            context["comment_user_name"] = "%s %s" % (request.user.first_name, request.user.last_name)
        context["create_date"] = project.create_datetime.date()
        context["views_count"] = project.views
        context["ranking"] = ranking
        context["detail_type_text"] = "projet"
        context["up_votes"] = up_votes
        context["down_votes"] = down_votes

        context["title_css_class"] = "detail_project_title"
        context["subtitle"] = "Projet"
        context["body_class"] = "body_projet"


        visitor = Visitor.objects.get(pk=request.session["visitor_id"])

        similar_projects = CityProject.objects.filter(~Q(id=kwargs["project_id"]))[:4]
        # This handy syntax translates to a LIMIT 4 query!
        
        # Fetching the vote (integers) of the user for each project:
        votes = [ \
            ["", ""] if (v is None or v.vote==0) \
            else \
                ["active-vote", ""] if v.vote>0 else ["", "active-vote"] \
            for v in
                [p.cityprojectvote_set.all().filter(visitor=visitor).first() \
                    for p in similar_projects\
                ] \
        ]
        context["similar_projects_and_votes"] = list(zip(similar_projects, votes))

        return render(request, 'mainApp/detailView.html', context)

class AddNewCommentView(generic.View):
    def post(self, request, *args, **kwargs):
        if "comment" not in request.POST \
            or "model_name" not in request.POST \
            or "id" not in request.POST \
        :
            return HttpResponseRedirect(reverse('mainApp:index', args=()))

        print("request.POST =", request.POST)
        response = {
            "result": "success",
        }
        visitor = Visitor.objects.get(pk=request.session["visitor_id"])
        if request.POST["model_name"] == "proposition":
            proposition = Proposition.objects.get(pk=request.POST["id"])
            comment = PropositionComment(proposition=proposition)
        elif request.POST["model_name"] == "project":
            project = CityProject.objects.get(pk=request.POST["id"])
            comment = CityProjectComment(project=project)

        comment.visitor = visitor
        comment.comment = request.POST["comment"]
        comment.validated = False
        comment.name_displayed = False
        validation_text = "Votre commentaire va être validé aussitôt que " \
            + "possible."

        if request.user.is_authenticated:
            user = User.objects.get(pk=int(request.user.id))
            comment.user = user

            if "publish_name" in request.POST \
                and request.POST["publish_name"]=="true" \
            :
                comment.name_displayed = True
                comment.validated = True
                validation_text = "Votre commentaire, publié en votre nom, a " \
                    + "été automatiquement validé et est affiché ci-dessous."
        comment.save()

        # If the comment is validated (i.e. authenticated and non-anonymous)
        # then the BE should respond it to the FE:
        if comment.validated:
            response["comment"] = render_comment(comment);

        response["message"] = "Merci pour votre commentaire !<br>" \
            + validation_text

        return JsonResponse(response);
class PropositionView(generic.View):

    def get(self, request, *args, **kwargs):
        proposition = Proposition.objects.get(pk=kwargs["proposition_id"])

        proposition.views += 1
        proposition.save()

        orderedPropositions = Proposition.objects.order_by('-views')
        rank = "?"
        for i, p in enumerate(orderedPropositions):
            if p == proposition:
                # zero-starting python index => into human one-starting index:
                rank = i+1
        ranking = "%d / %d" % (rank, len(orderedPropositions))

        validated_comments = PropositionComment.objects.filter(proposition=proposition, validated=True).order_by("-create_datetime")

        signatures = len(proposition.propositionsignature_set.all())

        context = \
            _contextifyDetail(proposition)


        rendered_authenticated_comments = []
        rendered_anynymous_comments = []
        for comment in validated_comments:
            if comment.name_displayed:
                rendered_authenticated_comments.append(render_comment(comment))
            else:
                rendered_anynymous_comments.append(render_comment(comment))

        context["authenticated_comments"] = rendered_authenticated_comments
        context["anynymous_comments"] = rendered_anynymous_comments
        context["model_name"] = "proposition"
        context["id"] = proposition.id


        context["login_next_url"] = reverse('mainApp:propositionDetail', args=(),
            kwargs={'proposition_id': proposition.id})
        context["comment_user_name"] = None
        if request.user.is_authenticated:
            context["comment_user_name"] = "%s %s" % (request.user.first_name, request.user.last_name)
        context["create_date"] = proposition.create_datetime
        context["views_count"] = proposition.views
        context["ranking"] = ranking
        context["detail_type_text"] = "projet"
        context["signatures"] = signatures

        context["title_css_class"] = "detail_proposition_title"
        context["subtitle"] = "Proposition"
        context["body_class"] = "body_proposition"

        return render(request, 'mainApp/detailView.html', context)

class AddNewProposition(generic.View):
    def post(self, request, *args, **kwargs):
        user = None
        if request.user.is_authenticated:
            user = User.objects.get(pk=int(request.user.id))

        if "title" in request.POST and \
            "description" in request.POST and \
            user is not None:

            # Computing the summary:
            """
            parser = PlaintextParser.from_string(request.POST["description"],
                Tokenizer(LANGUAGE))
            stemmer = Stemmer(LANGUAGE)
            summarizer = LsaSummarizer(stemmer)
            summarizer.stop_words = get_stop_words(LANGUAGE)
            summary = " ".join([str(x) for x in summarizer(parser.document,
                SUMMARY_SENTENCES_COUNT)])
            """
            summary = request.POST["description"][0:250]
            image = None
            if "image" in request.FILES:
                image = request.FILES["image"]

            proposition = Proposition(title=request.POST["title"],
                description=request.POST["description"],
                summary=summary,
                image=image,
                author=user,
            )
            proposition.approved = False
            proposition.save()
            request.session["message"] = "Nouvelle proposition ajoutée."
            messages.add_message(request, messages.INFO, "Nouvelle proposition ajoutée. Elle sera validée ausi publiée dès que possible.")
        else:
            messages.add_message(request, messages.ERROR, "Impossible d'enregistrer votre proposition. Merci de remplir tous les champs.")

        return HttpResponseRedirect(reverse('mainApp:index', args=()))

    def get(self, request, *args, **kwargs):
        title = ""
        if "title" in request.GET:
            title = request.GET["title"]

        user_full_name =  ""
        if request.user.is_authenticated:
            user = User.objects.get(pk=int(request.user.id))
            user_full_name = "%s %s" % (user.first_name, user.last_name)
        return render(request, "mainApp/new_proposition.html", {
            "title": title,
            "user_full_name": user_full_name,
        })

class SearchView(generic.View):
    def post(self, request, *args, **kwargs):
        """
        This function searches the propositions and projects given a provided text
        input from the search bar.
        """

        if not "content" in request.POST:
            return JsonResponse({"result": "refused"});

        suggestions = []

        propositions = Proposition.objects.filter(Q(title__icontains=request.POST["content"]))
        suggestions += [{"url": reverse('mainApp:propositionDetail', kwargs={'proposition_id': p.id}), "title": """<span class="badge bg-success rounded-pill">Proposition</span> """+p.title} for p in propositions]


        cityProjects = CityProject.objects.filter(Q(title__icontains=request.POST["content"]))
        suggestions += [{"url": reverse('mainApp:projectDetail', kwargs={'project_id': p.id}), "title": """<span class="badge bg-info rounded-pill">Projet</span> """+p.title} for p in cityProjects]

        # Sorting and keeping at max 5 items:
        suggestions = sorted(suggestions, key=lambda x: x["title"])[:min(len(suggestions),5)]

        return JsonResponse({
            "result": "ok",
            "suggestions": suggestions
            });


def create_sharing_div(target_url, link_title, share_title):
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
    return "<div><h4 class=\"popup_title\">" + share_title +"</h4>" \
        + """<p class="syndication_p pb-5">""" + shareButtons + """</p></div>"""

class AddVoteComment(generic.View):
    def _create_stats_div(self, project_id):
        project = CityProject.objects.get(pk=project_id)
        up_votes = len(
            [v.vote for v in project.cityprojectvote_set.all().filter(vote=1)])
        down_votes = len(
            [v.vote for v in project.cityprojectvote_set.all().filter(vote=-1)])

        # Saving the poll answers:
        questions = CityProjectQuestion.objects.filter(project=project)
        question_answers_html = "<h4 class=\"popup_title pt-5\">Réponses complémentaires</h4>"
        for question in questions:
            res = "Pas encore assez de réponse..."
            if question.type != "TEXTAREA":
                if question.type == "YES_NO":
                    try:
                        res = statistics.mean([x.numeric_answer for x in question.cityprojectanswer_set.all()])
                        res = "{:.0f}".format((1-res)*100) + "% de oui"
                    except:
                        pass
                elif question.type == "RATING_STARS":
                    try:
                        res = statistics.mean([x.numeric_answer for x in question.cityprojectanswer_set.all()])
                        res = str(res) +"/5 étoile(s)"
                    except:
                        pass
                elif question.type == "RATING_10_5_0":
                    try:
                        res = ""
                        total = len(question.cityprojectanswer_set.all())
                        for i, desc in enumerate(CityProjectQuestion.ratings_10_5_0_values):
                            qty = len(question.cityprojectanswer_set.all().filter(
                                numeric_answer=i)
                            )
                            res += "{:.2f}".format(qty/total*100) + "% " + desc + "<br>"
                    except:
                        pass

                question_answers_html += """<div class="textarea_group mt-2">
                    <p>%s</p>
                    <p><strong>%s</strong></p>
                </div>""" % (question.question_statement, res)

        return "<h4 class=\"popup_title\">Résultats actuel du vote</h4>" \
            + """<div class="pb-5"><div class="result_div_positive"><img src="static/mainApp/images/upvote.png" alt="" /><span>%d vote%s positif%s</span></div>""" % (up_votes, "s" if up_votes>1 else "", "s" if up_votes>1 else "") \
            + """<div class="result_div_negative"><img src="static/mainApp/images/downvote.png" alt="" /><span>%d vote%s négatif%s</span></div>""" % (down_votes, "s" if down_votes>1 else "", "s" if down_votes>1 else "")  \
            + question_answers_html \
            + "</div>"

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

        # Saving the poll answers:
        questions = CityProjectQuestion.objects.filter(project=project)
        for question in questions:
            if "answer_%d" % question.id in request.POST \
                and len(request.POST["answer_%d" % question.id]) > 0:
                # save answer...
                answer, created = CityProjectAnswer.objects.get_or_create(
                    question=question,
                    visitor=visitor)
                if question.type == "TEXTAREA":
                    answer.text_answer = request.POST["answer_%d" % question.id]
                else:
                    answer.numeric_answer = request.POST["answer_%d" % question.id]

                # Saving the user if he is authenticated:
                if request.user.is_authenticated:
                    user = User.objects.get(pk=int(request.user.id))
                    answer.user = user
                answer.save()

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
        image_filename = "summary_upvote.png"
        action_div = create_sharing_div(project_url, project.title, "Partage ce projet")

        if vote.vote < 0:
            image_filename = "summary_downvote.png"
            action_div = "<div class=\"changement\"><img src=\"static/mainApp/images/motivation.png\" alt=\"\" /> Crée le changement</div>"
            proposition_title = urllib.parse.quote(
                "Proposition contre le projet "+project.title)
            additional_div = """<a href="%s?title=%s" class="create_proposition_from_popup">Lancer une proposition ?</a></div>""" \
                % (
                    reverse('mainApp:addNewProposition', args=()),
                    proposition_title
                )


        anonymous_text = """<p class="mt-5 text-start">Tu n'es pas enregistrés, ton vote a été enregistré anonymement. En te connectant, tu donneras plus de poids à votre voix:</p><a href="%s" class="account_button mb-5">S'authentifier</a>""" % reverse('login', args=())

        if request.user.is_authenticated:
            anonymous_text = ""


        return JsonResponse({
            "result": "ok",
            "popup_title": "Merci pour votre vote!",
            "popup_content":
                "<img src=\"static/mainApp/images/" + image_filename + "\" alt=\"Merci!\" class=\"popup_center_image\" />" \
                + "<div class=\"text-start\">"
                    + action_div \
                    + self._create_stats_div(request.POST["project_id"]) \
                    + additional_div \
                    + anonymous_text \
                + "</div>",
            "popup_next_button_vals": []
        })

class VoteProject(generic.View):

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


        if request.user.is_authenticated:
            user = User.objects.get(pk=int(request.user.id))
            vote_object.user = user

        vote_object.save()


        image_filename = "thanks_upvote.png"
        if vote > 0:
            textarea_precaption = "Je trouve le projet <strong>%s</strong> très bien car:" % project.title
        else:
            textarea_precaption = "Je n'aime pas le projet <strong>%s</strong> car:" % project.title
            image_filename = "thanks_downvote.png"

        questions_html = ""
        questions = CityProjectQuestion.objects.filter(project=int(project_id))
        for question in questions:
            existing_answer_numeric = None
            # Trying to get the existing answer:
            try:
                existing_user_answers = question.cityprojectanswer_set \
                    .get(visitor=visitor).numeric_answer
            except:
                pass
            form_fields = ""
            field_name = "answer_%d" % question.id
            if question.type == "YES_NO" or question.type == "RATING_10_5_0":
                if question.type == "YES_NO":
                    texts = CityProjectQuestion.yes_no
                elif question.type == "RATING_10_5_0":
                    texts = CityProjectQuestion.ratings_10_5_0_values
                for i,t in enumerate(texts):
                    css_id = "%s_%d" % (field_name, i)
                    checked = ""
                    if i == existing_answer_numeric:
                        checked = " checked=\"checked\""
                    form_fields += """<input type="radio" name="%s" value="%d" id="%s"%s class="additional_questions_input"> <label for="%s">%s</label> """ % (field_name, i, css_id, checked, css_id, t)
            elif question.type == "TEXTAREA":
                form_fields = """<textarea name="%s" class="additional_questions_input"></textarea>""" % field_name
            elif question.type == "RATING_STARS":
                form_fields = """<div class="rate">"""
                for i in range(5, 0, -1):
                    checked = ""
                    if i == existing_answer_numeric:
                        checked = " checked=\"checked\""
                    form_fields += """<input type="radio" id="%s_%d"%s name="%s" value="%d" class="additional_questions_input" />
                    <label for="%s_%d" title="text">%d stars</label>
                    """ % (field_name, i, checked, field_name, i, field_name, i, i)
                form_fields += """</div>"""

            questions_html += """<div class="textarea_group mt-2">
                <p>%s</p>
                %s
            </div>""" % (question.question_statement, form_fields)

        popup_content = """<img src="static/mainApp/images/%s" alt="merci pour ton vote" class="popup_center_image" />
           <form action="%s">
            <div class="textarea_group">
                <label>%s</label>
                <textarea name="comment"></textarea>
            </div>
            %s
            <input type="hidden" name="project_id" value="%d" />
            <input type="hidden" name="vote" value="%d" />
            </form>""" % (image_filename, reverse('mainApp:addVoteComment', args=()), textarea_precaption, questions_html, project_id, vote)

        return JsonResponse({
            "result": "OK",
            "new_vote": new_vote,
            "vote":vote_object.vote,
            "popup_title": "Merci pour votre vote",
            "popup_content": popup_content,
            "popup_next_button_vals": ["Voir les résultats", "Commenter et voir les résultats"],
        });


class SignProposition(generic.View):

    def _is_account_complete(registered_user):
        return registered_user.zip_code is not None \
            and registered_user.city is not None \
            and registered_user.birth_year is not None

    def getSummaryViewContent(self, request, proposition):
        proposition_url = "%s://%s" \
            % (request.scheme, request.META["HTTP_HOST"]) \
            + reverse('mainApp:propositionDetail', kwargs={
                'proposition_id': proposition.id
            })

        return """<img src="/static/mainApp/images/thanks_signature.png" alt="" class="signature_popup_image">""" \
            + """<p class="pt-3">Merci <strong>%s %s</strong>,<br>grâce à toi les choses<br>bougent dans la commune!</p>""" \
                % (request.user.first_name, request.user.last_name) \
            + create_sharing_div(proposition_url, proposition.title, "Partage cette proposition")


    def post(self, request, *args, **kwargs):
        """
        Post a new signature (from the confirmation popup).
        """

        if not "proposition_id" in request.POST or \
            not request.user.is_authenticated \
        :
            return JsonResponse({"result": "refused", "reason": "1"});

        if not SignProposition._is_account_complete(request.user.registereduser):
            registered_user_form = \
                RegisteredUserForm(
                    request.POST,
                    request.FILES,
                    instance=request.user.registereduser
                )
            registered_user_form.save()
        if not SignProposition._is_account_complete(request.user.registereduser):
            return JsonResponse({"result": "refused", "reason": "2"});


        proposition_id = int(request.POST["proposition_id"])
        proposition = Proposition.objects.get(pk=proposition_id)

        signature, is_new_signature = PropositionSignature.objects.get_or_create(
            proposition=proposition,
            user=request.user
        )
        signature.save()

        return JsonResponse({
            "result": "OK",
            "popup_title": "Proposition signée",
            "popup_content": self.getSummaryViewContent(request, proposition),
            "popup_next_button_vals": []
            });

    def get(self, request, *args, **kwargs):
        """
        Return the popup content of a signature confirmation
        """
        if not request.user.is_authenticated:
            return JsonResponse({
                "result": "redirect",
                "url": reverse('login', args=())+"?next="+reverse('mainApp:index', args=())
            });


        if "proposition_id" not in request.GET:
            return JsonResponse({"result": "refused"});

        proposition_id = int(request.GET["proposition_id"])
        proposition = Proposition.objects.get(pk=proposition_id)

        # If the signature already exists, then we display the summary view:
        try:
            signature = PropositionSignature.objects.get(
                proposition=proposition,
                user=request.user
            )
            return JsonResponse({
                "result": "OK",
                "popup_title": "Proposition déjà signée",
                "popup_content": self.getSummaryViewContent(request, proposition)
                });
        except ObjectDoesNotExist as e:
            pass

        registered_user_form = None
        if not SignProposition._is_account_complete(request.user.registereduser):
            registered_user_form = \
                RegisteredUserForm(instance=request.user.registereduser)


        popup_content = render_to_string("mainApp/sign_proposition.html", {
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "proposition_title": proposition.title,
                "proposition_id": proposition_id,
                'registered_user_form': registered_user_form,
            })

        return JsonResponse({
            "result": "OK",
            "popup_title": "Confirmation de signature",
            "popup_content": popup_content,
            "popup_next_button_vals": ["Signer la proposition"]*2
            });
