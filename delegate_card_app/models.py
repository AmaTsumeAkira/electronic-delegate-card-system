# delegate_card_app/models.py
from django.db import models
from django.conf import settings # 用于获取当前用户 (如果需要记录审核人)

class Delegate(models.Model):
    APPROVAL_CHOICES = [
        ('pending', '待审核'),
        ('approved', '审核通过'),
        ('rejected', '审核不通过'),
    ]

    # ... (现有字段: name, gender, photo, political_status, student_id, etc.) ...
    name = models.CharField(max_length=100, verbose_name="姓名")
    gender_choices = [('M', '男'), ('F', '女'), ('O', '其他')] # 确保与表单一致
    gender = models.CharField(max_length=1, choices=gender_choices, verbose_name="性别")
    photo = models.ImageField(upload_to='delegate_photos/', blank=True, null=True, verbose_name="照片")
    political_status = models.CharField(max_length=50, verbose_name="政治面貌")
    student_id = models.CharField(max_length=20, unique=True, verbose_name="学号")
    delegation = models.CharField(max_length=100, verbose_name="代表团")
    class_name = models.CharField(max_length=100, verbose_name="班级")
    card_number = models.CharField(max_length=50, unique=True, verbose_name="证件编号", blank=True, null=True) # 允许 blank 和 null，因为可能在审核通过后才最终确定
    valid_until = models.DateField(verbose_name="有效期至", blank=True, null=True)
    issuing_authority = models.CharField(max_length=200, verbose_name="发证单位", blank=True, null=True)
    issue_date = models.DateField(verbose_name="签发日期", blank=True, null=True)

    is_checked_in = models.BooleanField(default=False, verbose_name="是否已签到")
    check_in_time = models.DateTimeField(null=True, blank=True, verbose_name="签到时间")

    # 新增审核相关字段
    approval_status = models.CharField(
        max_length=10,
        choices=APPROVAL_CHOICES,
        default='pending', # 新提交的默认为“待审核”
        verbose_name="审核状态"
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, # 如果审核员被删除，保留审核记录但审核人置空
        null=True, blank=True,
        related_name='approved_delegates',
        verbose_name="审核人"
    )
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name="审核时间")
    approval_remarks = models.TextField(blank=True, null=True, verbose_name="审核备注") # 用于记录不通过原因等

    # (可选) 新增提交时间
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="提交时间", null=True, blank=True)


    def __str__(self):
        return f"{self.name} ({self.student_id}) - {self.get_approval_status_display()}"

    class Meta:
        verbose_name = "代表信息" # 修改为更通用
        verbose_name_plural = "代表信息管理"
        ordering = ['-submitted_at', 'name'] # 按提交时间降序，姓名升序