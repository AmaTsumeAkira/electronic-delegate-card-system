# delegate_card_app/forms.py
from django import forms
# delegate_card_app/forms.py
from django import forms
from .models import Delegate # 假设你的 Delegate 模型已定义

# 定义下拉选项
POLITICAL_STATUS_CHOICES = [
    ('', '---- 请选择 ----'),
    ('中共党员', '中共党员'),
    ('中共预备党员', '中共预备党员'),
    ('共青团员', '共青团员'),
    ('群众', '群众'),
]

DELEGATION_CHOICES = [
    ('', '---- 请选择 ----'),
    ('第一代表团', '第一代表团'),
    ('第二代表团', '第二代表团'),
    ('第三代表团', '第三代表团'),
    # ...更多代表团
]

# 班级选项可以很多，这里仅作示例。实际应用中，这些选项可能来自数据库或更复杂的配置。
CLASS_NAME_CHOICES = [
    ('', '---- 请选择 ----'),
    ('2022级计算机应用技术一班', '2022级计算机应用技术一班'),
    ('2022级计算机应用技术二班', '2022级计算机应用技术二班'),
    ('2022级计算机应用技术三班', '2022级计算机应用技术三班'),
    ('2022级信息安全技术应用一班', '2022级信息安全技术应用一班'),
    ('2022级信息安全技术应用二班', '2022级信息安全技术应用二班'),
    ('2022级软件技术一班', '2022级软件技术一班'),
    ('2022级软件技术二班', '2022级软件技术二班'),
    ('2023级计算机应用技术一班', '2023级计算机应用技术一班'),
    ('2023级计算机应用技术二班', '2023级计算机应用技术二班'),
    ('2023级信息安全技术应用一班', '2023级信息安全技术应用一班'),
    ('2023级信息安全技术应用二班', '2023级信息安全技术应用二班'),
    ('2023级软件技术一班', '2023级软件技术一班'),
    ('2023级软件技术二班', '2023级软件技术二班'),
    ('2023级移动应用开发一班', '2023级移动应用开发一班'),
    ('2023级移动应用开发二班', '2023级移动应用开发二班'),
    ('2024级计算机技术应用一班', '2024级计算机技术应用一班'),
    ('2024级计算机技术应用二班', '2024级计算机技术应用二班'),
    ('2024级信息安全技术应用班', '2024级信息安全技术应用班'),
    ('2024级软件技术一班', '2024级软件技术一班'),
    ('2024级软件技术二班', '2024级软件技术二班'),
    ('2024级移动应用开发班', '2024级移动应用开发班'),
]

GENDER_CHOICES = [
    ('', '---- 请选择 ----'),
    ('M', '男'),
    ('F', '女'),
]

class DelegateSubmissionForm(forms.ModelForm):
    # 使下拉选项的第一个为空值提示
    political_status = forms.ChoiceField(choices=POLITICAL_STATUS_CHOICES, required=True, label="政治面貌")
    delegation = forms.ChoiceField(choices=DELEGATION_CHOICES, required=True, label="代表团")
    class_name = forms.ChoiceField(choices=CLASS_NAME_CHOICES, required=True, label="班级")
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=True, label="性别")

    # 对照片字段进行自定义，使其不是必填项，但如果提供了，需要是图片
    photo = forms.ImageField(label="免冠照片 (小于5MB)", required=True, help_text="请上传清晰的近期免冠证件照，JPG或PNG格式。")


    class Meta:
        model = Delegate
        fields = [
            'name', 'gender', 'photo', 'political_status',
            'student_id', 'delegation', 'class_name'
        ]
        # 固定的字段 (发证单位, 签发日期, 有效期) 和自动生成的 (证件编号) 不应在此表单中
        # 它们将在视图中处理

        widgets = {
            'name': forms.TextInput(attrs={'placeholder': '请输入真实姓名'}),
            'student_id': forms.TextInput(attrs={'placeholder': '请输入12位学号'}),
            # 其他字段的 widget 可以根据需要自定义
        }
        labels = {
            'name': '姓名',
            'student_id': '学号',
        }

    def clean_student_id(self):
        student_id = self.cleaned_data.get('student_id')
        # 示例验证：学号必须是12位数字 (根据你的实际学号规则调整)
        if student_id and (not student_id.isdigit() or len(student_id) != 12):
            raise forms.ValidationError("学号必须是12位数字。")

        # 检查学号是否已存在 (防止重复提交)
        if Delegate.objects.filter(student_id=student_id).exists():
            # 如果是更新操作，需要排除当前对象自身
            # if self.instance and self.instance.student_id == student_id:
            #     pass # 允许学号不变
            # else:
            raise forms.ValidationError("该学号已被注册，请勿重复提交或检查学号是否正确。")
        return student_id

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo:
            # 限制图片大小 (例如 2MB)
            if photo.size > 5 * 1024 * 1024:
                raise forms.ValidationError("图片文件过大，请上传小于5MB的图片。")
            # 可以在这里添加更多图片类型或尺寸的验证
        elif not self.instance.pk: # 如果是新建记录且没有提供照片 (如果照片是必填的)
             raise forms.ValidationError("请上传免冠照片。")
        return photo
    
class DelegateQueryForm(forms.Form):
    name = forms.CharField(label='姓名', max_length=100, required=True,
                           widget=forms.TextInput(attrs={'placeholder': '请输入您的姓名', 'class': 'form-input-style'}))
    student_id = forms.CharField(label='学号', max_length=20, required=True,
                                 widget=forms.TextInput(attrs={'placeholder': '请输入您的学号', 'class': 'form-input-style'}))
    # 你可以在 widget attrs 中添加 Tailwind CSS 类，或者在模板中直接渲染字段并添加类