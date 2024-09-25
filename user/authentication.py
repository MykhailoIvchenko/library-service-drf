from rest_framework.authentication import TokenAuthentication


class CustomHeaderTokenAuthentication(TokenAuthentication):
    keyword = "Authorize"
