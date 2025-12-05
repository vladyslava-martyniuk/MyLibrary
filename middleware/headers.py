from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from security_token import CSRFProtectionMiddleware

csrf_protection = CSRFProtectionMiddleware()
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
	async def dispatch(self, request, call_next):
		if request.method in ['GET', 'HEAD', 'OPTIONS']:
			response = await call_next(request)
			response.headers['GET-SECURE'] = 'true'
			return response
		
		csrf_token = request.headers.get("X-CSRF-Token")
		session_id = "session-id"

		if not csrf_protection.validate_csrf_token(csrf_token, session_id):
			return Response("CSRF token missing or invalid", status_code=403)
		
		response = await call_next(request)
		response.headers['POST-SECURE'] = 'true'
		return response