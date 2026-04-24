from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Profile
from .serializers import (
    DashboardLayoutSerializer,
    ProfileMeSerializer,
    ProfileMeWriteSerializer,
    ProfilePublicSerializer,
)

User = get_user_model()


class ProfileMeView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "patch", "head", "options"]

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return ProfileMeWriteSerializer
        return ProfileMeSerializer

    def get_object(self):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        return profile

    def perform_update(self, serializer):
        serializer.save()
        dn = self.request.data.get("display_name")
        if dn is not None:
            self.request.user.display_name = str(dn)[:150]
            self.request.user.save(update_fields=["display_name"])


class DashboardLayoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        return Response({"layout": profile.dashboard_layout})

    def patch(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        ser = DashboardLayoutSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        profile.dashboard_layout = ser.validated_data["layout"]
        profile.save(update_fields=["dashboard_layout", "updated_at"])
        return Response({"layout": profile.dashboard_layout})


class ProfileDetailView(generics.RetrieveAPIView):
    serializer_class = ProfilePublicSerializer
    lookup_field = "user_id"
    lookup_url_kwarg = "user_id"

    def get_queryset(self):
        return Profile.objects.select_related("user").all()

    def get_object(self):
        uid = self.kwargs["user_id"]
        user = get_object_or_404(User, pk=uid)
        profile, _ = Profile.objects.get_or_create(user=user)
        return profile

    def retrieve(self, request, *args, **kwargs):
        profile = self.get_object()
        if profile.privacy == Profile.Privacy.PRIVATE and (
            not request.user.is_authenticated or request.user.id != profile.user_id
        ):
            return Response(
                {"detail": "Профиль скрыт."},
                status=status.HTTP_404_NOT_FOUND,
            )
        ser = self.get_serializer(profile)
        return Response(ser.data)
