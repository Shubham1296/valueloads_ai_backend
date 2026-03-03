from rest_framework import serializers
from .models import DataExport


class DataExportSerializer(serializers.ModelSerializer):
    requested_by_name = serializers.CharField(source='requested_by.full_name', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = DataExport
        fields = '__all__'
        read_only_fields = ['id', 'status', 'file_url', 'file_size_bytes', 'row_count',
                            'created_at', 'completed_at']
