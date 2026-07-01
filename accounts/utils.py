from rest_framework_simplejwt.tokens import RefreshToken

def get_tokens_for_user(user):
    """
    Utility function to generate JWT access and refresh tokens for a given user.
    """
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
