from rest_framework import generics, permissions
from .models import Profile
from .serializers import ProfileSerializer, ProfileUpdateSerializer, AvatarUpdateSerializer
from .permissions import IsOwnerOrReadOnly


class ProfileListView(generics.ListAPIView):
    """List all developer profiles with filtering."""
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Profile.objects.all()
        
        # Manual filtering based on query params
        skills = self.request.query_params.get('skills')
        location = self.request.query_params.get('location')
        exp_level = self.request.query_params.get('experience_level')

        if skills:
            queryset = queryset.filter(skills__icontains=skills)
        if location:
            queryset = queryset.filter(location__iexact=location)
        if exp_level:
            queryset = queryset.filter(experience_level__iexact=exp_level)
            
        return queryset


class ProfileDetailView(generics.RetrieveAPIView):
    """Retrieve a single profile by ID."""
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]


class ProfileUpdateView(generics.UpdateAPIView):
    serializer_class = ProfileUpdateSerializer
    # Ensuring the user is logged in and is the owner
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_object(self):
        return self.request.user.profile


class AvatarUpdateView(generics.UpdateAPIView):
    serializer_class = AvatarUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_object(self):
        return self.request.user.profile