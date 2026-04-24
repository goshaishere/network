from rest_framework import generics, permissions
from rest_framework.response import Response

from .serializers import UploadedFileSerializer


class MediaUploadView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UploadedFileSerializer

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        obj = serializer.instance
        url = request.build_absolute_uri(obj.file.url) if obj.file else ""
        return Response({"id": obj.id, "url": url})
