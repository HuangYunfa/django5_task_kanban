"""
Users应用视图
用户管理相关视图
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView, PasswordChangeView,
    PasswordChangeDoneView
)
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site

from .models import User, UserProfile
from .forms import (
    CustomUserCreationForm, CustomLoginForm, CustomPasswordResetForm,
    UserProfileForm, UserProfileExtendedForm, CustomPasswordChangeForm,
    AvatarUploadForm, UserSearchForm
)

User = get_user_model()


# 用户认证视图
class UserRegisterView(CreateView):
    """用户注册视图"""
    model = User
    form_class = CustomUserCreationForm
    template_name = 'users/auth/register.html'
    success_url = reverse_lazy('users:login')
    
    def dispatch(self, request, *args, **kwargs):
        # 已登录用户不能访问注册页面
        if request.user.is_authenticated:
            return redirect('common:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('注册成功！请登录您的账户。'))
        
        # 发送邮箱验证邮件
        if self.object.email:
            self.send_verification_email(self.object)
            
        return response
    
    def send_verification_email(self, user):
        """发送邮箱验证邮件"""
        current_site = get_current_site(self.request)
        subject = _('验证您的邮箱地址')
        message = render_to_string('users/emails/email_verification.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
            'protocol': 'https' if self.request.is_secure() else 'http',
        })
        
        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
            messages.info(self.request, _('验证邮件已发送到您的邮箱，请查收。'))
        except Exception as e:
            messages.warning(self.request, _('邮件发送失败，请稍后重试。'))


class UserLoginView(LoginView):
    """用户登录视图"""
    form_class = CustomLoginForm
    template_name = 'users/auth/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('common:dashboard')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('欢迎回来！'))
        
        # 记录登录IP
        user = form.get_user()
        user.last_login_ip = self.get_client_ip()
        user.save(update_fields=['last_login_ip'])
        
        return response
    
    def get_client_ip(self):
        """获取客户端IP地址"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class UserLogoutView(LogoutView):
    """用户登出视图"""
    next_page = reverse_lazy('users:login')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.success(request, _('您已成功登出。'))
        return super().dispatch(request, *args, **kwargs)


class CustomPasswordResetView(PasswordResetView):
    """密码重置视图"""
    form_class = CustomPasswordResetForm
    template_name = 'users/auth/password_reset.html'
    email_template_name = 'users/emails/password_reset_email.html'
    subject_template_name = 'users/emails/password_reset_subject.txt'
    success_url = reverse_lazy('users:password_reset_done')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    """密码重置完成视图"""
    template_name = 'users/auth/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """密码重置确认视图"""
    template_name = 'users/auth/password_reset_confirm.html'
    success_url = reverse_lazy('users:password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    """密码重置完成视图"""
    template_name = 'users/auth/password_reset_complete.html'


# 邮箱验证视图
def email_verify(request, uidb64, token):
    """邮箱验证视图"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.email_verified = True
        user.save()
        messages.success(request, _('邮箱验证成功！'))
        login(request, user)
        return redirect('common:dashboard')
    else:
        messages.error(request, _('邮箱验证链接无效或已过期。'))
        return redirect('users:login')


class UserPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """用户密码修改视图"""
    form_class = CustomPasswordChangeForm
    template_name = 'users/auth/password_change.html'
    success_url = reverse_lazy('users:password_change_done')


class UserPasswordChangeDoneView(LoginRequiredMixin, TemplateView):
    """密码修改完成视图"""
    template_name = 'users/auth/password_change_done.html'


def email_verification_view(request, uidb64, token):
    """邮箱验证视图"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.email_verified = True
        user.save(update_fields=['email_verified'])
        messages.success(request, _('邮箱验证成功！'))
        return redirect('users:login')
    else:
        messages.error(request, _('邮箱验证链接无效或已过期。'))
        return redirect('users:register')


# 用户管理视图
class UserListView(LoginRequiredMixin, ListView):
    """用户列表视图"""
    model = User
    template_name = 'users/list.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                username__icontains=search
            ) | queryset.filter(
                email__icontains=search
            ) | queryset.filter(
                nickname__icontains=search
            )
        return queryset.order_by('-date_joined')


class UserDetailView(LoginRequiredMixin, DetailView):
    """用户详情视图"""
    model = User
    template_name = 'users/detail.html'
    context_object_name = 'user_detail'


class UserProfileView(LoginRequiredMixin, UpdateView):
    """用户资料视图"""
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('users:profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('个人资料更新成功！'))
        return response


class UserPreferencesView(LoginRequiredMixin, UpdateView):
    """用户偏好设置视图"""
    model = User
    form_class = UserProfileExtendedForm
    template_name = 'users/preferences.html'
    success_url = reverse_lazy('users:preferences')
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('偏好设置更新成功！'))
        return response


class UserSettingsView(LoginRequiredMixin, TemplateView):
    """用户设置视图"""
    template_name = 'users/settings.html'


# 新增的用户管理视图
class AvatarUploadView(LoginRequiredMixin, UpdateView):
    """头像上传视图"""
    model = User
    form_class = AvatarUploadForm
    template_name = 'users/avatar_upload.html'
    success_url = reverse_lazy('users:profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('头像上传成功！'))
        return response


def ajax_user_search(request):
    """Ajax用户搜索视图"""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form = UserSearchForm(request.GET)
        if form.is_valid():
            users = form.search_users()[:10]  # 限制返回10个结果
            results = []
            for user in users:
                results.append({
                    'id': user.id,
                    'username': user.username,
                    'nickname': user.nickname or '',
                    'email': user.email,
                    'avatar_url': user.get_avatar_url(),
                    'display_name': user.get_display_name(),
                })
            return JsonResponse({'results': results})
    return JsonResponse({'results': []})


def resend_verification_email(request):
    """重新发送验证邮件"""
    if request.method == 'POST' and request.user.is_authenticated:
        if not request.user.email_verified:
            # 重新发送验证邮件的逻辑
            current_site = get_current_site(request)
            subject = _('验证您的邮箱地址')
            message = render_to_string('users/emails/email_verification.html', {
                'user': request.user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(request.user.pk)),
                'token': default_token_generator.make_token(request.user),
                'protocol': 'https' if request.is_secure() else 'http',
            })
            
            try:
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [request.user.email])
                messages.success(request, _('验证邮件已重新发送，请查收。'))
            except Exception as e:
                messages.error(request, _('邮件发送失败，请稍后重试。'))
        else:
            messages.info(request, _('您的邮箱已经验证过了。'))
    
    return redirect('users:profile')


class UserActivityView(LoginRequiredMixin, TemplateView):
    """用户活动记录视图"""
    template_name = 'users/activity.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 这里可以添加用户活动日志的查询
        # context['activities'] = ActivityLog.objects.filter(user=self.request.user)[:20]
        return context


class UserNotificationsView(LoginRequiredMixin, TemplateView):
    """用户通知视图"""
    template_name = 'users/notifications.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 这里可以添加用户通知的查询
        # context['notifications'] = Notification.objects.filter(recipient=self.request.user)
        return context


def mark_notification_read(request, notification_id):
    """标记通知为已读"""
    if request.method == 'POST' and request.user.is_authenticated:
        # 这里添加标记通知为已读的逻辑
        # notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
        # notification.is_read = True
        # notification.read_at = timezone.now()
        # notification.save()
        messages.success(request, _('通知已标记为已读。'))
    
    return redirect('users:notifications')


class UserTeamsView(LoginRequiredMixin, TemplateView):
    """用户团队视图"""
    template_name = 'users/teams.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 这里可以添加用户所属团队的查询
        # context['team_memberships'] = TeamMembership.objects.filter(user=self.request.user, status='active')
        return context


class UserBoardsView(LoginRequiredMixin, TemplateView):
    """用户看板视图"""
    template_name = 'users/boards.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 这里可以添加用户相关看板的查询
        # context['owned_boards'] = Board.objects.filter(owner=self.request.user)
        # context['member_boards'] = Board.objects.filter(members__user=self.request.user)
        return context


def deactivate_account(request):
    """停用账户"""
    if request.method == 'POST' and request.user.is_authenticated:
        # 这里添加停用账户的逻辑
        user = request.user
        user.is_active = False
        user.save()
        logout(request)
        messages.success(request, _('您的账户已被停用。'))
        return redirect('users:login')
    
    return redirect('users:settings')
