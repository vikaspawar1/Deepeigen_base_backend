from django.http import HttpResponseForbidden
from django.urls import reverse
from  admin_honeypot import urls
class RestrictAdminHoneypotMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        honeypot_url = '/adminsecurelogin/admin_honeypot/loginattempt/'
        
        if request.path==honeypot_url and not request.user.is_superadmin:
            return HttpResponseForbidden("<h2>Access Forbidden </h2>")
        return response
    