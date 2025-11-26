from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")

            if refresh_token:
                from rest_framework_simplejwt.tokens import RefreshToken

                token = RefreshToken(refresh_token)
                token.blacklist()

            return Response({"detail": "Logged Out"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"detail": {f"{e} error occured"}}, status=status.HTTP_400_BAD_REQUEST
            )
