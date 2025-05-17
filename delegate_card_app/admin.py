# delegate_card_app/admin.py
from django.contrib import admin
from django.utils import timezone
from .models import Delegate

@admin.register(Delegate)
class DelegateAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'student_id', 'delegation', 'class_name',
        'approval_status', 'card_number', 'submitted_at', 'approved_by', 'approved_at'
    )
    list_filter = ('approval_status', 'delegation', 'class_name', 'gender')
    search_fields = ('name', 'student_id', 'card_number', 'approval_remarks')
    readonly_fields = ('submitted_at', 'approved_by', 'approved_at') # 这些字段通常不应手动修改

    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'gender', 'student_id', 'photo',
                       'political_status', 'delegation', 'class_name')
        }),
        ('证件信息 (审核通过后填写/生成)', {
            'fields': ('card_number', 'issuing_authority', 'issue_date', 'valid_until'),
             'classes': ('collapse',), # 默认折叠，审核通过时展开
        }),
        ('签到信息', {
            'fields': ('is_checked_in', 'check_in_time'),
            'classes': ('collapse',),
        }),
        ('审核状态 (管理员操作)', {
            'fields': ('approval_status', 'approval_remarks', 'submitted_at', 'approved_by', 'approved_at'),
        }),
    )

    actions = ['approve_selected', 'reject_selected', 'mark_as_pending']

    def save_model(self, request, obj, form, change):
        # 如果审核状态从非'approved'变为'approved'，并且之前没有审核人/时间
        if 'approval_status' in form.changed_data and obj.approval_status == 'approved':
            if not obj.approved_by: # 只有在首次通过时记录
                obj.approved_by = request.user
            obj.approved_at = timezone.now()
            # (可选) 在这里触发证件编号生成和固定字段填充逻辑，如果不是在申报时就完成的话
            # if not obj.card_number:
            #     from .views import generate_next_card_number # 避免循环导入
            #     obj.card_number = generate_next_card_number()
            # if not obj.issue_date:
            #     obj.issue_date = date(2025, 5, 22) # 假设固定
            # if not obj.valid_until:
            #     obj.valid_until = date(2025, 5, 30)
            # if not obj.issuing_authority:
            #     obj.issuing_authority = "山西财专信息科技学院分团委"

        # 如果状态变为 pending 或 rejected，可以清除审核人和审核时间
        elif 'approval_status' in form.changed_data and obj.approval_status != 'approved':
            obj.approved_by = None
            obj.approved_at = None

        super().save_model(request, obj, form, change)

    @admin.action(description='审核通过选中的代表')
    def approve_selected(self, request, queryset):
        for obj in queryset:
            if obj.approval_status != 'approved':
                obj.approval_status = 'approved'
                obj.approved_by = request.user
                obj.approved_at = timezone.now()
                # (可选) 在这里也加入证件编号生成等逻辑
                # if not obj.card_number:
                #    from .views import generate_next_card_number
                #    obj.card_number = generate_next_card_number()
                # ... (其他字段填充) ...
                obj.save()
        self.message_user(request, f"{queryset.count()} 条记录已审核通过。")

    @admin.action(description='审核不通过选中的代表 (请填写备注)')
    def reject_selected(self, request, queryset):
        # 对于不通过，最好引导管理员去详情页填写不通过原因
        # 这里仅简单标记，备注需要在编辑页面填写
        updated_count = queryset.update(
            approval_status='rejected',
            approved_by=None, # 或 request.user 如果想记录谁操作的不通过
            approved_at=timezone.now()
        )
        self.message_user(request, f"{updated_count} 条记录已标记为审核不通过。请记得为每条记录填写审核备注。")

    @admin.action(description='标记为待审核')
    def mark_as_pending(self, request, queryset):
        updated_count = queryset.update(
            approval_status='pending',
            approved_by=None,
            approved_at=None
        )
        self.message_user(request, f"{updated_count} 条记录已标记为待审核。")

admin.site.site_header = "电子代表证管理后台"
admin.site.site_title = "代表证管理"
admin.site.index_title = "欢迎使用代表证管理系统"