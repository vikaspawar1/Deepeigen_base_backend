from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .utils import get_tokens_for_user

@api_view(['POST'])
@permission_classes([]) # Custom auth logic inside
def jwt_login(request):
    """
    API endpoint for JWT login (standard credentials)
    """
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response({'success': False, 'message': 'Email and password required'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(email=email, password=password)
    if user:
        if not user.is_active:
            return Response({'success': False, 'message': 'Account is disabled'}, status=status.HTTP_403_FORBIDDEN)
            
        tokens = get_tokens_for_user(user)
        return Response({
            'success': True,
            'access': tokens['access'],
            'refresh': tokens['refresh'],
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        })
    return Response({'success': False, 'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([])
def jwt_refresh(request):
    """
    API endpoint to refresh access token
    """
    refresh_token = request.data.get('refresh')
    if not refresh_token:
        return Response({'success': False, 'message': 'Refresh token required'}, status=status.HTTP_400_BAD_REQUEST)
        
    try:
        refresh = RefreshToken(refresh_token)
        return Response({
            'success': True,
            'access': str(refresh.access_token)
        })
    except Exception as e:
        return Response({'success': False, 'message': 'Invalid or expired refresh token'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def jwt_logout(request):
    """
    API endpoint to logout by blacklisting the refresh token
    """
    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'success': False, 'message': 'Refresh token required'}, status=status.HTTP_400_BAD_REQUEST)
            
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'success': True, 'message': 'Logged out successfully'})
    except Exception as e:
        return Response({'success': False, 'message': 'Invalid refresh token or already blacklisted'}, status=status.HTTP_400_BAD_REQUEST)
