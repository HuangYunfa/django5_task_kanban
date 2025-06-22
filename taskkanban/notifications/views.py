from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404
from django.views.generic import (
    TemplateView, ListView, CreateView, UpdateView, DeleteView, FormView
)
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
from django.conf import settings

from .models import (
    EmailTemplate, UserNotificationPreference, EmailNotification,
    NotificationQueue, UnsubscribeToken
)
from .services import EmailService, NotificationTrigger
from .forms import (
    NotificationPreferencesForm, EmailTemplateForm, TestEmailForm
)


class NotificationPreferencesView(LoginRequiredMixin, TemplateView):
    """用户通知偏好设置页面"""
    template_name = 'notifications/preferences.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        preference = EmailService.get_user_preference(self.request.user)
        context['form'] = NotificationPreferencesForm(instance=preference)
        context['preference'] = preference
        return context


class UpdateNotificationPreferencesView(LoginRequiredMixin, FormView):
    """更新用户通知偏好"""
    form_class = NotificationPreferencesForm
    template_name = 'notifications/preferences.html'
    success_url = reverse_lazy('notifications:preferences')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        preference = EmailService.get_user_preference(self.request.user)
        kwargs['instance'] = preference
        return kwargs
    
    def form_valid(self, form):
        form.save()
        messages.success(self.request, _('通知偏好设置已更新'))
        return super().form_valid(form)


class UnsubscribeView(TemplateView):
    """退订页面"""
    template_name = 'notifications/unsubscribe.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        token = kwargs.get('token')
        
        try:
            unsubscribe_token = UnsubscribeToken.objects.get(token=token)
            if unsubscribe_token.is_valid():
                context['token'] = unsubscribe_token
                context['valid'] = True
            else:
                context['valid'] = False
                context['error'] = _('退订链接已过期或已使用')
        except UnsubscribeToken.DoesNotExist:
            context['valid'] = False
            context['error'] = _('无效的退订链接')
        
        return context
    
    def post(self, request, *args, **kwargs):
        token = kwargs.get('token')
        
        if EmailService.process_unsubscribe(token):
            return redirect('notifications:unsubscribe_success')
        else:
            messages.error(request, _('退订失败，请稍后再试'))
            return self.get(request, *args, **kwargs)


class UnsubscribeSuccessView(TemplateView):
    """退订成功页面"""
    template_name = 'notifications/unsubscribe_success.html'


class TrackEmailReadView(TemplateView):
    """邮件阅读追踪"""
    def get(self, request, *args, **kwargs):
        notification_id = kwargs.get('notification_id')
        
        try:
            notification = EmailNotification.objects.get(id=notification_id)
            notification.mark_as_read()
        except EmailNotification.DoesNotExist:
            pass
        
        # 返回1x1像素透明图片
        response = HttpResponse(content_type='image/png')
        response['Content-Length'] = '43'
        response.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\xdac\xf8\x0f\x00\x00\x01\x00\x01\x00\x18\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82')
        return response


class TrackEmailClickView(TemplateView):
    """邮件点击追踪"""
    def get(self, request, *args, **kwargs):
        notification_id = kwargs.get('notification_id')
        redirect_url = request.GET.get('url', '/')
        
        try:
            notification = EmailNotification.objects.get(id=notification_id)
            notification.mark_as_clicked()
        except EmailNotification.DoesNotExist:
            pass
        
        return redirect(redirect_url)


class NotificationHistoryView(LoginRequiredMixin, ListView):
    """用户通知历史"""
    model = EmailNotification
    template_name = 'notifications/history.html'
    context_object_name = 'notifications'
    paginate_by = 20
    
    def get_queryset(self):
        return EmailNotification.objects.filter(
            recipient=self.request.user
        ).order_by('-created_at')


class NotificationDetailView(LoginRequiredMixin, TemplateView):
    """通知详情"""
    template_name = 'notifications/detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        notification_id = kwargs.get('notification_id')
        
        notification = get_object_or_404(
            EmailNotification,
            id=notification_id,
            recipient=self.request.user
        )
        
        context['notification'] = notification
        return context


# 管理员功能视图

class AdminRequiredMixin(UserPassesTestMixin):
    """管理员权限验证"""
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class EmailTemplateListView(AdminRequiredMixin, ListView):
    """邮件模板列表"""
    model = EmailTemplate
    template_name = 'notifications/admin/template_list.html'
    context_object_name = 'templates'
    paginate_by = 20


class EmailTemplateCreateView(AdminRequiredMixin, CreateView):
    """创建邮件模板"""
    model = EmailTemplate
    form_class = EmailTemplateForm
    template_name = 'notifications/admin/template_form.html'
    success_url = reverse_lazy('notifications:admin_templates')
    
    def form_valid(self, form):
        messages.success(self.request, _('邮件模板创建成功'))
        return super().form_valid(form)


class EmailTemplateUpdateView(AdminRequiredMixin, UpdateView):
    """编辑邮件模板"""
    model = EmailTemplate
    form_class = EmailTemplateForm
    template_name = 'notifications/admin/template_form.html'
    success_url = reverse_lazy('notifications:admin_templates')
    
    def form_valid(self, form):
        messages.success(self.request, _('邮件模板更新成功'))
        return super().form_valid(form)


class EmailTemplateDeleteView(AdminRequiredMixin, DeleteView):
    """删除邮件模板"""
    model = EmailTemplate
    template_name = 'notifications/admin/template_confirm_delete.html'
    success_url = reverse_lazy('notifications:admin_templates')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, _('邮件模板删除成功'))
        return super().delete(request, *args, **kwargs)


class TestEmailSendView(AdminRequiredMixin, FormView):
    """测试邮件发送"""
    form_class = TestEmailForm
    template_name = 'notifications/admin/test_send.html'
    success_url = reverse_lazy('notifications:admin_test_send')
    
    def form_valid(self, form):
        try:
            # 创建测试通知
            notification = EmailService.create_notification(
                recipient=form.cleaned_data['recipient'],
                template_type=form.cleaned_data['template_type'],
                context={
                    'test_message': form.cleaned_data.get('test_message', '这是一封测试邮件'),
                    'sent_by': self.request.user,
                }
            )
            
            if notification:
                # 立即发送
                if EmailService.send_notification(notification):
                    messages.success(self.request, _('测试邮件发送成功'))
                else:
                    messages.error(self.request, _('测试邮件发送失败'))
            else:
                messages.warning(self.request, _('未创建通知，可能是用户关闭了相关通知'))
                
        except Exception as e:
            messages.error(self.request, f'发送失败: {str(e)}')
        
        return super().form_valid(form)


# API视图 (供前端Ajax调用)

class NotificationAPIView(LoginRequiredMixin, TemplateView):
    """通知API视图基类"""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            raise Http404
        return super().dispatch(request, *args, **kwargs)


class GetUnreadNotificationsView(NotificationAPIView):
    """获取未读通知数量"""
    
    def get(self, request, *args, **kwargs):
        count = EmailNotification.objects.filter(
            recipient=request.user,
            status='sent',
            read_at__isnull=True
        ).count()
        
        return JsonResponse({'unread_count': count})


class MarkNotificationReadView(NotificationAPIView):
    """标记通知为已读"""
    
    def post(self, request, *args, **kwargs):
        notification_id = request.POST.get('notification_id')
        
        try:
            notification = EmailNotification.objects.get(
                id=notification_id,
                recipient=request.user
            )
            notification.mark_as_read()
            return JsonResponse({'success': True})
        except EmailNotification.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Notification not found'})
