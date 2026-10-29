import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import User

def generate_jwt(user: User) -> str:
    payload = {
        'sub': str(user.id),
        'user_id': user.id,
        'name': user.name,
        'email': user.email,
        'role': user.role,
        'exp': datetime.now(timezone.utc) + timedelta(hours=12),
        'iat': datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

@api_view(['POST'])
def register_user(request):
    name = request.data.get('name', '').strip()
    email = request.data.get('email', '').strip().lower()
    password = request.data.get('password', '')

    if not name or not email or len(password) < 6:
        return Response({'error': 'Name, valid email, and password (min 6 chars) are required.'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email is already registered.'}, status=status.HTTP_409_CONFLICT)

    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user = User.objects.create(name=name, email=email, password=hashed_pw, role='customer')
    token = generate_jwt(user)
    return Response({
        'access_token': token,
        'token_type': 'bearer',
        'user': {'id': user.id, 'name': user.name, 'email': user.email, 'role': user.role}
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def login_user(request):
    email = request.data.get('email', '').strip().lower()
    password = request.data.get('password', '')

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)

    if user.is_blocked:
        return Response({'error': 'Your account has been suspended by an administrator.'}, status=status.HTTP_403_FORBIDDEN)

    if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        return Response({'error': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)

    token = generate_jwt(user)
    return Response({
        'access_token': token,
        'token_type': 'bearer',
        'user': {'id': user.id, 'name': user.name, 'email': user.email, 'role': user.role}
    })

@api_view(['POST'])
def logout_user(request):
    return Response({'message': 'Successfully logged out. Client token invalidated.'})

@api_view(['GET'])
def verify_token(request):
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return Response({'error': 'Missing Bearer token'}, status=status.HTTP_401_UNAUTHORIZED)
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return Response({'valid': True, 'payload': payload})
    except jwt.PyJWTError as exc:
        return Response({'valid': False, 'error': str(exc)}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
def list_users(request):
    users = User.objects.all().order_by('-created_at').values('id', 'name', 'email', 'role', 'is_blocked', 'created_at')
    return Response(list(users))

@api_view(['PATCH'])
def toggle_block_user(request, user_id: int):
    try:
        user = User.objects.get(id=user_id)
        if user.role == 'admin':
            return Response({'error': 'Cannot block an admin account.'}, status=status.HTTP_400_BAD_REQUEST)
        user.is_blocked = not user.is_blocked
        user.save()
        return Response({'id': user.id, 'name': user.name, 'is_blocked': user.is_blocked})
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
