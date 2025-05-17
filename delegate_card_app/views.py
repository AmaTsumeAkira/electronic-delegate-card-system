# 标准库导入
import re
from datetime import date
import json # 用于将数据传递给JS

# Django 框架导入
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseForbidden
from django.urls import reverse
from django.utils import timezone
from django.db.models import Max, Count, Q # Q对象用于复杂查询
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.serializers.json import DjangoJSONEncoder # 处理日期等特殊类型

# 第三方库导入 (Rest Framework)
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

# 本地应用导入
from .models import Delegate
from .serializers import DelegateSerializer
from .forms import DelegateQueryForm, DelegateSubmissionForm


# 辅助函数
def is_staff_user(user):
    return user.is_authenticated and user.is_staff

def generate_next_card_number():
    current_year = timezone.now().year
    year_prefix = str(current_year)

    delegates_this_year = Delegate.objects.filter(card_number__startswith=year_prefix)
    max_sequence_in_year = 0
    if delegates_this_year.exists():
        for delegate in delegates_this_year:
            card_num_str = delegate.card_number
            if card_num_str and card_num_str.startswith(year_prefix) and len(card_num_str) == len(year_prefix) + 3:
                try:
                    sequence_str = card_num_str[len(year_prefix):]
                    if sequence_str.isdigit():
                        sequence_val = int(sequence_str)
                        if sequence_val > max_sequence_in_year:
                            max_sequence_in_year = sequence_val
                except ValueError:
                    print(f"警告: 卡号 {card_num_str} 格式不符合预期 YYYYNNN。")
                    continue
    
    next_sequence = max_sequence_in_year + 1
    if next_sequence > 999:
        raise ValueError(f"年份 {current_year} 的代表证序列号已达到上限 (999)。请检查。")
    return f"{year_prefix}{str(next_sequence).zfill(3)}"

@user_passes_test(is_staff_user, login_url='/admin/login/')
def dashboard_view(request):
    return render(request, 'dashboard.html')

@user_passes_test(is_staff_user, login_url='/admin/login/')
def dashboard_data_api(request):
    total_delegates = Delegate.objects.count()
    approved_delegates_qs = Delegate.objects.filter(approval_status='approved')
    approved_delegates_count = approved_delegates_qs.count()
    pending_delegates_count = Delegate.objects.filter(approval_status='pending').count()
    rejected_delegates_count = Delegate.objects.filter(approval_status='rejected').count()

    checked_in_delegates_count = approved_delegates_qs.filter(is_checked_in=True).count()
    check_in_rate = (checked_in_delegates_count / approved_delegates_count * 100) if approved_delegates_count > 0 else 0

    kpi_data = {
        'total_delegates': total_delegates,
        'approved_delegates': approved_delegates_count,
        'pending_delegates': pending_delegates_count,
        'checked_in_delegates': checked_in_delegates_count,
        'check_in_rate': round(check_in_rate, 1),
    }

    approval_status_data = Delegate.objects.values('approval_status').annotate(value=Count('id')).order_by('approval_status')
    approval_status_map = dict(Delegate.APPROVAL_CHOICES)
    approval_status_distribution = [{'name': approval_status_map.get(item['approval_status'], item['approval_status']), 'value': item['value']} for item in approval_status_data]

    delegation_data = approved_delegates_qs.values('delegation').annotate(value=Count('id')).filter(value__gt=0).order_by('-value')
    delegation_distribution = [{'name': item['delegation'], 'value': item['value']} for item in delegation_data]

    political_status_data = approved_delegates_qs.values('political_status').annotate(value=Count('id')).filter(value__gt=0).order_by('-value')
    political_status_distribution = [{'name': item['political_status'], 'value': item['value']} for item in political_status_data]

    gender_data = approved_delegates_qs.values('gender').annotate(value=Count('id')).order_by('gender')
    gender_map = dict(Delegate.gender_choices)
    gender_distribution = [{'name': gender_map.get(item['gender'], item['gender']), 'value': item['value']} for item in gender_data]

    class_data = approved_delegates_qs.values('class_name').annotate(value=Count('id')).filter(value__gt=0).order_by('-value')
    class_distribution = [{'name': item['class_name'], 'value': item['value']} for item in class_data]

    response_data = {
        'timestamp': timezone.now().isoformat(),
        'kpi': kpi_data,
        'approval_status_distribution': approval_status_distribution,
        'delegation_distribution': delegation_distribution,
        'political_status_distribution': political_status_distribution,
        'gender_distribution': gender_distribution,
        'class_distribution': class_distribution,
    }
    return JsonResponse(response_data)

def navigation_page_view(request):
    return render(request, 'navigation.html')

@user_passes_test(is_staff_user, login_url='/admin/login/')
def delegate_list_view(request):
    delegates_qs = Delegate.objects.all()

    # KPI Calculations
    total_delegates_kpi = Delegate.objects.count()
    approved_delegates_qs_kpi = Delegate.objects.filter(approval_status='approved')
    approved_delegates_count_kpi = approved_delegates_qs_kpi.count()
    pending_delegates_count_kpi = Delegate.objects.filter(approval_status='pending').count()
    rejected_delegates_count_kpi = Delegate.objects.filter(approval_status='rejected').count()
    
    checked_in_delegates_count_kpi = approved_delegates_qs_kpi.filter(is_checked_in=True).count()
    check_in_rate_kpi = (checked_in_delegates_count_kpi / approved_delegates_count_kpi * 100) if approved_delegates_count_kpi > 0 else 0

    kpi_stats = {
        'total_delegates': total_delegates_kpi,
        'approved_delegates': approved_delegates_count_kpi,
        'pending_delegates': pending_delegates_count_kpi,
        'rejected_delegates': rejected_delegates_count_kpi,
        'checked_in_delegates': checked_in_delegates_count_kpi,
        'check_in_rate': round(check_in_rate_kpi, 1),
    }

    # 搜索
    search_query = request.GET.get('q', '').strip()
    if search_query:
        delegates_qs = delegates_qs.filter(
            Q(name__icontains=search_query) |
            Q(student_id__icontains=search_query) |
            Q(card_number__icontains=search_query) |
            Q(delegation__icontains=search_query)
        )

    # 筛选
    approval_status_filter = request.GET.get('approval_status', '')
    if approval_status_filter:
        delegates_qs = delegates_qs.filter(approval_status=approval_status_filter)

    is_checked_in_filter = request.GET.get('is_checked_in', '')
    if is_checked_in_filter:
        if is_checked_in_filter == 'true':
            delegates_qs = delegates_qs.filter(is_checked_in=True)
        elif is_checked_in_filter == 'false':
            delegates_qs = delegates_qs.filter(is_checked_in=False)
    
    delegation_filter = request.GET.get('delegation', '')
    if delegation_filter:
        delegates_qs = delegates_qs.filter(delegation=delegation_filter)

    # 排序
    sort_by = request.GET.get('sort_by', 'card_number') # Default sort by card_number (ascending)
    valid_sort_fields = ['name', '-name', 'student_id', '-student_id', 
                         'card_number', '-card_number', 'submitted_at', '-submitted_at',
                         'approval_status', '-approval_status', 'delegation', '-delegation']
    if sort_by not in valid_sort_fields:
        sort_by = 'card_number' 
    
    delegates_qs = delegates_qs.order_by(sort_by)
    
    distinct_delegations = Delegate.objects.order_by('delegation').values_list('delegation', flat=True).distinct()

    context = {
        'delegates': delegates_qs, 
        'page_title': "代表信息概览",
        'search_query': search_query,
        'approval_status_filter': approval_status_filter,
        'is_checked_in_filter': is_checked_in_filter,
        'delegation_filter': delegation_filter,
        'distinct_delegations': distinct_delegations,
        'current_sort_by': sort_by,
        'approval_choices': Delegate.APPROVAL_CHOICES,
        'kpi_stats': kpi_stats, # 将KPI数据添加到上下文中
    }
    return render(request, 'delegate_list.html', context)


def submit_delegate_info_view(request):
    success_message = None
    new_card_number_on_success = None

    if request.method == 'POST':
        form = DelegateSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                delegate_instance = form.save(commit=False)
                delegate_instance.issuing_authority = "山西财专信息科技学院分团委"
                delegate_instance.issue_date = date(2025, 5, 22)
                delegate_instance.valid_until = date(2025, 5, 30)
                delegate_instance.card_number = generate_next_card_number()
                delegate_instance.save()
                success_message = "您的信息已成功提交，请等待管理员审核！"
                new_card_number_on_success = delegate_instance.card_number
                form = DelegateSubmissionForm()
            except ValueError as ve:
                form.add_error(None, str(ve))
            except IntegrityError:
                form.add_error(None, "提交失败，可能因为证件编号或学号冲突，请尝试重新提交或联系管理员。")
            except Exception as e:
                print(f"Error saving delegate info: {e}")
                form.add_error(None, f"提交过程中发生系统错误，请稍后重试。")
    else:
        form = DelegateSubmissionForm()

    context = {
        'form': form,
        'success_message': success_message,
        'new_card_number': new_card_number_on_success,
    }
    return render(request, 'submit_delegate_info.html', context)

@login_required
def scan_checkin_view(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("您没有权限访问此页面。")
    return render(request, 'scan_checkin.html')

def query_delegate_view(request):
    form = DelegateQueryForm()
    message = None
    message_type = None
    approval_remarks_message = None

    if request.method == 'POST':
        form = DelegateQueryForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            student_id = form.cleaned_data['student_id']
            try:
                delegate = Delegate.objects.get(name=name, student_id=student_id)
                if delegate.approval_status == 'approved':
                    redirect_url = reverse('home') + f'?card_number={delegate.card_number}'
                    return redirect(redirect_url)
                elif delegate.approval_status == 'pending':
                    message = f"您好，{delegate.name}。您的代表资格申请正在审核中，请耐心等待。"
                    message_type = 'info' 
                elif delegate.approval_status == 'rejected':
                    message = f"您好，{delegate.name}。抱歉，您的代表资格申请未通过审核。"
                    message_type = 'warning'
                    if delegate.approval_remarks:
                        approval_remarks_message = f"审核备注：{delegate.approval_remarks}"
                    else:
                        approval_remarks_message = "审核备注：未提供具体原因。如有疑问，请联系分团委组织部。"
                else:
                    status_display = delegate.get_approval_status_display()
                    message = f"您好，{delegate.name}。您的代表资格当前状态为 “{status_display}”。请联系管理员获取更多信息。"
                    message_type = 'info'
            except Delegate.DoesNotExist:
                message = "未找到与您提交信息匹配的代表记录。请仔细核对姓名和学号。"
                message_type = 'error'
            except Delegate.MultipleObjectsReturned:
                message = "系统发现多条与您提交信息匹配的记录，数据异常。请联系管理员。"
                message_type = 'error'
            except Exception as e:
                print(f"Error querying delegate: {e}") 
                message = "查询过程中发生系统错误，请稍后重试或联系管理员。"
                message_type = 'error'
        else:
            message = "输入信息有误，请检查表单。"
            message_type = 'error'
    
    context = {
        'form': form,
        'message': message,
        'message_type': message_type,
        'approval_remarks_message': approval_remarks_message,
    }
    return render(request, 'query_delegate.html', context)

def home_page_view(request):
    card_number_from_url = request.GET.get('card_number')
    delegate_id_from_url = request.GET.get('delegate_id')
    context = {
        'card_number_from_url': card_number_from_url,
        'delegate_id_from_url': delegate_id_from_url,
    }
    return render(request, 'index.html', context)

class DelegateViewSet(viewsets.ModelViewSet):
    serializer_class = DelegateSerializer
    def get_queryset(self):
        if self.request.user.is_staff:
            return Delegate.objects.all()
        return Delegate.objects.filter(approval_status='approved')


    @action(detail=False, methods=['get'], url_path='by-card-number/(?P<card_num>[^/.]+)')
    def get_by_card_number(self, request, card_num=None):
        try:
            delegate = Delegate.objects.get(card_number=card_num, approval_status='approved')
            serializer = self.get_serializer(delegate)
            return Response(serializer.data)
        except Delegate.DoesNotExist:
            return Response({'error': '未找到该卡号的代表信息或代表未获批准。', 'found': False}, status=status.HTTP_404_NOT_FOUND)
        except Delegate.MultipleObjectsReturned:
             return Response({'error': '找到多个相同卡号的代表，数据异常。', 'found': False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='check-in', permission_classes=[permissions.IsAdminUser])
    def check_in(self, request, pk=None):
        try:
            delegate = Delegate.objects.get(pk=pk)
        except Delegate.DoesNotExist:
             return Response({'error': '代表不存在', 'status': 'not_found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e: 
            return Response({'error': f'获取代表对象时出错: {str(e)}', 'status': 'error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if delegate.approval_status != 'approved':
            status_display = delegate.get_approval_status_display()
            return Response({
                'status': 'not_approved',
                'message': f'代表 {delegate.name} ({delegate.student_id}) 尚未审核通过，无法签到。当前状态: {status_display}',
                'delegate_name': delegate.name,
                'check_in_time': None 
            }, status=status.HTTP_400_BAD_REQUEST)

        if delegate.is_checked_in:
            return Response({
                'status': 'already_checked_in',
                'message': '该代表已签到',
                'check_in_time': delegate.check_in_time.strftime('%Y-%m-%d %H:%M:%S') if delegate.check_in_time else None,
                'delegate_name': delegate.name
            }, status=status.HTTP_200_OK)

        try:
            delegate.is_checked_in = True
            delegate.check_in_time = timezone.now()
            delegate.save()
            return Response({
                'status': 'checked_in_successfully',
                'message': '签到成功',
                'check_in_time': delegate.check_in_time.strftime('%Y-%m-%d %H:%M:%S'),
                'delegate_name': delegate.name
            }, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error during check-in save for delegate {pk}: {e}")
            return Response({
                'status': 'error_saving',
                'message': f'保存签到信息时发生错误。',
                'delegate_name': delegate.name,
                'check_in_time': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)