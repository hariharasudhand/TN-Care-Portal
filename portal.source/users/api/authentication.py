from rest_framework.authentication import TokenAuthentication
from users.api.models import MyOwnToken


class MyOwnTokenAuthentication(TokenAuthentication):
    model = MyOwnToken
