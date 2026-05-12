from rest_framework import viewsets, permissions
from .models import Update, ChangeRequest
from .serializers import UpdateSerializer, ChangeRequestSerializer

class UpdateViewSet(viewsets.ModelViewSet):
    queryset = Update.objects.all()
    serializer_class = UpdateSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        # Only staff can access; could further restrict if needed
        return Update.objects.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class ChangeRequestViewSet(viewsets.ModelViewSet):
    queryset = ChangeRequest.objects.all()
    serializer_class = ChangeRequestSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        # Optionally filter by user/requester
        return ChangeRequest.objects.all()

    def perform_create(self, serializer):
        # If user is authenticated, set as requester
        if self.request.user.is_authenticated:
            serializer.save(requester=self.request.user)
        else:
            serializer.save()
