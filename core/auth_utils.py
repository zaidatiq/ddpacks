# core/auth_utils.py
import jwt
import datetime
from django.http import JsonResponse
from django.conf import settings
from .models import User

JWT_SECRET = settings.SECRET_KEY
JWT_EXPIRY_HOURS = getattr(settings, 'JWT_EXPIRY_HOURS', 24)


def generate_jwt(user):
    payload = {
        'id': user.id,
        'email': user.email,
        'role': 'admin' if user.is_superuser else 'user',
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=JWT_EXPIRY_HOURS),
        'iat': datetime.datetime.now(datetime.timezone.utc)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')


def decode_jwt(token):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def jwt_required(view_func):
    def wrapper(request, *args, **kwargs):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Unauthorized'}, status=401)

        token = auth_header.split(' ')[1]
        decoded = decode_jwt(token)
        if not decoded:
            return JsonResponse({'error': 'Invalid or expired token'}, status=401)

        try:
            user = User.objects.get(id=decoded['id'])
            request.user = user
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

        return view_func(request, *args, **kwargs)
    return wrapper
