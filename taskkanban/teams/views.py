"""
Teams应用视图
团队管理相关视图
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponseForbidden
from django.utils.translation import gettext as _
from django.utils import timezone
from django.core.paginator import Paginator

from .models import Team, TeamMembership, TeamInvitation
from .forms import TeamForm, TeamMembershipForm, TeamInvitationForm, TeamSearchForm


class TeamListView(LoginRequiredMixin, ListView):
    """团队列表视图"""
    model = Team
    template_name = 'teams/list.html'
    context_object_name = 'teams'
    paginate_by = 12

    def get_queryset(self):
        """获取团队查询集"""
        user = self.request.user
        queryset = Team.objects.select_related('created_by').prefetch_related('memberships')
        
        # 获取用户相关的团队（成员身份或公开团队）
        user_teams = Team.objects.filter(
            Q(memberships__user=user, memberships__status='active') |
            Q(is_public=True)
        ).distinct()
        
        # 处理搜索
        form = TeamSearchForm(self.request.GET)
        if form.is_valid():
            search = form.cleaned_data.get('search')
            if search:
                user_teams = user_teams.filter(
                    Q(name__icontains=search) | 
                    Q(description__icontains=search)
                )
            
            is_public = form.cleaned_data.get('is_public')
            if is_public:
                user_teams = user_teams.filter(is_public=is_public == 'true')
            
            role = form.cleaned_data.get('role')
            if role:
                user_teams = user_teams.filter(                    memberships__user=user,
                    memberships__role=role,
                    memberships__status='active'
                )
        
        return user_teams.annotate(
            total_members=Count('memberships', filter=Q(memberships__status='active'))
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = TeamSearchForm(self.request.GET)
        
        # 获取用户的团队统计
        user = self.request.user
        context['my_teams_count'] = TeamMembership.objects.filter(
            user=user, 
            status='active'
        ).count()
        context['invitations_count'] = TeamInvitation.objects.filter(
            invitee=user, 
            status='pending'
        ).count()
        
        return context


class TeamCreateView(LoginRequiredMixin, CreateView):
    """创建团队视图"""
    model = Team
    form_class = TeamForm
    template_name = 'teams/create.html'
    success_url = reverse_lazy('teams:list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, _('团队创建成功！'))
        return super().form_valid(form)


class TeamDetailView(LoginRequiredMixin, DetailView):
    """团队详情视图"""
    model = Team
    template_name = 'teams/detail.html'
    context_object_name = 'team'

    def get_queryset(self):
        """限制访问权限"""
        user = self.request.user
        return Team.objects.filter(
            Q(memberships__user=user, memberships__status='active') |
            Q(is_public=True)
        ).distinct().select_related('created_by').prefetch_related(
            'memberships__user',
            'memberships__invited_by'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team = self.object
        user = self.request.user
        
        # 获取用户在该团队的成员关系
        try:
            user_membership = team.memberships.get(user=user, status='active')
            context['user_membership'] = user_membership
            context['is_admin'] = user_membership.is_admin
        except TeamMembership.DoesNotExist:
            context['user_membership'] = None
            context['is_admin'] = False
        
        # 获取团队成员列表
        members = team.memberships.filter(status='active').select_related('user', 'invited_by')
        context['members'] = members
        context['member_count'] = members.count()
        
        # 获取待处理的邀请（管理员可见）
        if context['is_admin']:
            context['pending_invitations'] = team.invitations.filter(
                status='pending'
            ).select_related('inviter', 'invitee').order_by('-created_at')
        
        return context


class TeamUpdateView(LoginRequiredMixin, UpdateView):
    """编辑团队视图"""
    model = Team
    form_class = TeamForm
    template_name = 'teams/edit.html'

    def get_queryset(self):
        """只有管理员可以编辑"""
        user = self.request.user
        return Team.objects.filter(
            memberships__user=user,
            memberships__role__in=['owner', 'admin'],
            memberships__status='active'
        ).distinct()

    def get_success_url(self):
        return reverse('teams:detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, _('团队信息更新成功！'))
        return super().form_valid(form)


class TeamMemberView(LoginRequiredMixin, TemplateView):
    """团队成员管理视图"""
    template_name = 'teams/members.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team_id = kwargs.get('pk')
        team = get_object_or_404(Team, pk=team_id)
        user = self.request.user
        
        # 检查权限
        try:
            user_membership = team.memberships.get(user=user, status='active')
            if not user_membership.is_admin:
                raise PermissionError("无权限管理成员")
        except TeamMembership.DoesNotExist:
            raise PermissionError("不是团队成员")
        
        context['team'] = team
        context['user_membership'] = user_membership
        
        # 获取成员列表
        members = team.memberships.filter(status='active').select_related('user', 'invited_by')
        context['members'] = members
        
        # 获取邀请表单
        context['invitation_form'] = TeamInvitationForm()
        
        # 获取待处理邀请
        context['pending_invitations'] = team.invitations.filter(
            status='pending'
        ).select_related('inviter', 'invitee')
        
        return context


class TeamInviteView(LoginRequiredMixin, View):
    """团队邀请视图"""
    
    def post(self, request, pk):
        team = get_object_or_404(Team, pk=pk)
        user = request.user
        
        # 检查权限
        try:
            membership = team.memberships.get(user=user, status='active')
            if not membership.is_admin:
                return HttpResponseForbidden(_('无权限邀请成员'))
        except TeamMembership.DoesNotExist:
            return HttpResponseForbidden(_('不是团队成员'))
        
        form = TeamInvitationForm(request.POST, team=team, inviter=user)
        if form.is_valid():
            invitation = form.save()
            messages.success(request, _('邀请发送成功！'))
            
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'success': True, 'message': _('邀请发送成功！')})
        else:
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'success': False, 'errors': form.errors})
            else:
                for error in form.errors.values():
                    messages.error(request, error[0])
        
        return redirect('teams:members', pk=team.pk)


class TeamJoinView(LoginRequiredMixin, View):
    """加入团队视图（处理邀请）"""
    
    def post(self, request, pk):
        invitation = get_object_or_404(TeamInvitation, pk=pk)
        user = request.user
        
        # 验证邀请
        if invitation.invitee != user:
            return HttpResponseForbidden(_('无效的邀请'))
        
        if invitation.status != 'pending':
            messages.error(request, _('邀请已处理或已过期'))
            return redirect('teams:list')
        
        if invitation.is_expired:
            invitation.status = 'expired'
            invitation.save()
            messages.error(request, _('邀请已过期'))
            return redirect('teams:list')
        
        action = request.POST.get('action')
        
        if action == 'accept':
            # 接受邀请
            invitation.status = 'accepted'
            invitation.responded_at = timezone.now()
            invitation.save()
            
            # 创建团队成员关系
            TeamMembership.objects.create(
                team=invitation.team,
                user=user,
                role=invitation.role,
                status='active',
                invited_by=invitation.inviter,
                joined_at=timezone.now()
            )
            
            messages.success(request, _('成功加入团队！'))
            return redirect('teams:detail', pk=invitation.team.pk)
            
        elif action == 'decline':
            # 拒绝邀请
            invitation.status = 'declined'
            invitation.responded_at = timezone.now()
            invitation.save()
            
            messages.info(request, _('已拒绝邀请'))
            return redirect('teams:list')
        
        return redirect('teams:list')


class TeamLeaveView(LoginRequiredMixin, View):
    """离开团队视图"""
    
    def post(self, request, pk):
        team = get_object_or_404(Team, pk=pk)
        user = request.user
        
        try:
            membership = team.memberships.get(user=user, status='active')
            
            # 所有者不能直接离开，需要先转让所有权
            if membership.role == 'owner':
                messages.error(request, _('所有者不能直接离开团队，请先转让所有权'))
                return redirect('teams:detail', pk=team.pk)
            
            # 更新成员状态为非活跃
            membership.status = 'inactive'
            membership.save()
            
            messages.success(request, _('已离开团队'))
            
        except TeamMembership.DoesNotExist:
            messages.error(request, _('你不是该团队的成员'))
        
        return redirect('teams:list')


class MyInvitationsView(LoginRequiredMixin, ListView):
    """我的邀请列表"""
    model = TeamInvitation
    template_name = 'teams/my_invitations.html'
    context_object_name = 'invitations'
    paginate_by = 10

    def get_queryset(self):
        return TeamInvitation.objects.filter(
            invitee=self.request.user,
            status='pending'
        ).select_related('team', 'inviter').order_by('-created_at')
