class LoginHistoryMiddleware:
    """Enregistre la dernière connexion de l'utilisateur."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            from .models import LoginHistory
            if request.session.get('login_recorded') is None:
                LoginHistory.objects.create(
                    user=request.user,
                    ip_address=self._get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                )
                request.session['login_recorded'] = True
        return self.get_response(request)

    def _get_client_ip(self, request):
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        if xff:
            return xff.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
