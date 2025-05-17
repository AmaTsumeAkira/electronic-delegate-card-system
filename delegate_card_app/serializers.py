# delegate_card_app/serializers.py
from rest_framework import serializers
from .models import Delegate

class DelegateSerializer(serializers.ModelSerializer):
    # 如果你的 photo 字段存储的是相对路径，DRF 会自动处理成完整的 URL (前提是 MEDIA_URL 配置正确)
    # photo_url = serializers.ImageField(source='photo', read_only=True) # 或者直接用 photo 字段

    class Meta:
        model = Delegate
        fields = [
            'id', 'name', 'gender', 'photo', # 'photo_url'
            'political_status', 'student_id', 'delegation',
            'class_name', 'card_number', 'valid_until',
            'issuing_authority', 'issue_date',
            'is_checked_in', 'check_in_time'
        ]
        # 可以为特定字段添加额外参数，例如只读
        # read_only_fields = ('is_checked_in', 'check_in_time')