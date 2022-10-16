from .models import *

class UserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # If no session, we create one:
        if not request.session.session_key:
            request.session.save()

        # If no temporary user object saved, we create one and mark its id in
        # the session:
        if not "visitor_id" in request.session:
            visitor = Visitor()
            visitor.save()
            request.session["visitor_id"] = visitor.id

        # Todo: add logic here for the registered user
        return self.get_response(request)
