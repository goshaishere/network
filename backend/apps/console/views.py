from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

User = get_user_model()


class AdminUsersStubView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        qs = User.objects.order_by("id")[:50]
        data = [
            {"id": u.id, "email": u.email, "display_name": u.display_name, "is_staff": u.is_staff}
            for u in qs
        ]
        return Response(data)


class AdminRolesStubView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response(
            [
                {"slug": "user", "name": "Пользователь"},
                {"slug": "admin", "name": "Администратор"},
            ]
        )
