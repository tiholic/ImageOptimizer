from rest_framework import serializers
from .models import StorageProvider


class StorageProviderSerializer(serializers.ModelSerializer):
    """Serializer for StorageProvider model"""
    
    credentials = serializers.JSONField(write_only=True, required=False)
    provider_type_display = serializers.CharField(source='get_provider_type_display', read_only=True)
    
    class Meta:
        model = StorageProvider
        fields = [
            'id', 'name', 'provider_type', 'provider_type_display',
            'is_default', 'is_active', 'config', 'credentials',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        credentials = validated_data.pop('credentials', {})
        user = self.context['request'].user
        
        storage_provider = StorageProvider.objects.create(
            user=user,
            **validated_data
        )
        
        if credentials:
            storage_provider.set_credentials(credentials)
            storage_provider.save()
        
        return storage_provider
    
    def update(self, instance, validated_data):
        credentials = validated_data.pop('credentials', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if credentials:
            instance.set_credentials(credentials)
        
        instance.save()
        return instance
    
    def validate(self, data):
        """Validate provider-specific requirements"""
        provider_type = data.get('provider_type', self.instance.provider_type if self.instance else None)
        credentials = data.get('credentials', {})
        
        # Validate required credentials based on provider type
        if provider_type == 's3':
            required_creds = ['access_key_id', 'secret_access_key']
            required_config = ['bucket', 'region']
        elif provider_type == 'azure':
            required_creds = ['account_name', 'account_key']
            required_config = ['container']
        elif provider_type == 'gcs':
            required_creds = ['credentials_json']
            required_config = ['bucket']
        elif provider_type == 'sftp':
            required_creds = ['host', 'username']
            required_config = ['remote_path']
        else:
            return data
        
        # Only validate credentials if being updated
        if credentials:
            missing_creds = [cred for cred in required_creds if cred not in credentials]
            if missing_creds:
                raise serializers.ValidationError({
                    'credentials': f"Missing required credentials for {provider_type}: {', '.join(missing_creds)}"
                })
        
        # Validate config
        config = data.get('config', self.instance.config if self.instance else {})
        missing_config = [conf for conf in required_config if conf not in config]
        if missing_config:
            raise serializers.ValidationError({
                'config': f"Missing required config for {provider_type}: {', '.join(missing_config)}"
            })
        
        return data


class StorageProviderListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing storage providers"""
    
    provider_type_display = serializers.CharField(source='get_provider_type_display', read_only=True)
    
    class Meta:
        model = StorageProvider
        fields = [
            'id', 'name', 'provider_type', 'provider_type_display',
            'is_default', 'is_active', 'created_at'
        ]
