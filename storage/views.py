from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import StorageProvider
from .serializers import StorageProviderSerializer, StorageProviderListSerializer


class StorageProviderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing storage providers
    
    list: Get all storage providers for the authenticated user
    create: Create a new storage provider
    retrieve: Get details of a specific storage provider
    update: Update a storage provider
    partial_update: Partially update a storage provider
    destroy: Delete a storage provider
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return StorageProvider.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return StorageProviderListSerializer
        return StorageProviderSerializer
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set this storage provider as default"""
        storage_provider = self.get_object()
        storage_provider.is_default = True
        storage_provider.save()
        
        serializer = self.get_serializer(storage_provider)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """Test connection to the storage provider"""
        storage_provider = self.get_object()
        
        try:
            from .backends import get_storage_backend
            backend = get_storage_backend(storage_provider)
            
            # Try to check if a dummy path exists (this tests connectivity)
            backend.exists('_connection_test_')
            
            return Response({
                'status': 'success',
                'message': 'Connection successful'
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Connection failed: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
