class TaskBatchOperationView(LoginRequiredMixin, View):
    """任务批量操作API"""
    
    def post(self, request):
        """批量操作处理"""
        try:
            # 尝试解析JSON数据
            if request.content_type == 'application/json':
                import json
                data = json.loads(request.body)
                task_ids = data.get('task_ids', [])
                operation = data.get('action')  # 使用action而不是operation
                
                # 从JSON数据中获取其他参数
                new_status = data.get('new_status')
                new_priority = data.get('new_priority')
                new_list_id = data.get('new_list_id')
                assignee_id = data.get('assignee_id')
            else:
                # 处理表单数据
                task_ids = request.POST.getlist('task_ids')
                operation = request.POST.get('action', request.POST.get('operation'))
                
                # 从表单数据中获取其他参数
                new_status = request.POST.get('new_status')
                new_priority = request.POST.get('new_priority')
                new_list_id = request.POST.get('new_list_id')
                assignee_id = request.POST.get('assignee_id', request.POST.get('user_id'))
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        
        if not task_ids:
            return JsonResponse({
                'success': False,
                'error': 'No tasks selected'
            }, status=400)
        
        if not operation:
            return JsonResponse({
                'success': False,
                'error': 'No operation specified'
            }, status=400)
        
        # 验证任务权限
        tasks = []
        for task_id in task_ids:
            try:
                task = Task.objects.get(id=task_id)
                if not self.has_task_edit_access(task, request.user):
                    return JsonResponse({
                        'success': False,
                        'error': f'权限不足，无法操作任务 {task_id}'
                    }, status=403)
                tasks.append(task)
            except Task.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': f'Task {task_id} not found'
                }, status=404)
        
        # 执行批量操作
        try:
            from django.db import transaction
            with transaction.atomic():
                if operation == 'delete':
                    count = len(tasks)
                    for task in tasks:
                        task.is_archived = True  # 软删除
                        task.save(update_fields=['is_archived', 'updated_at'])
                    return JsonResponse({
                        'success': True,
                        'message': f'Successfully deleted {count} tasks'
                    })
                
                elif operation == 'change_status':
                    if not new_status or new_status not in dict(Task.STATUS_CHOICES):
                        return JsonResponse({
                            'success': False,
                            'error': 'Invalid status'
                        }, status=400)
                    
                    count = 0
                    for task in tasks:
                        task.status = new_status
                        task.save(update_fields=['status', 'updated_at'])
                        count += 1
                    
                    return JsonResponse({
                        'success': True,
                        'message': f'Successfully updated {count} tasks'
                    })
                
                elif operation == 'change_priority':
                    if not new_priority or new_priority not in dict(Task.PRIORITY_CHOICES):
                        return JsonResponse({
                            'success': False,
                            'error': 'Invalid priority'
                        }, status=400)
                    
                    count = 0
                    for task in tasks:
                        task.priority = new_priority
                        task.save(update_fields=['priority', 'updated_at'])
                        count += 1
                    
                    return JsonResponse({
                        'success': True,
                        'message': f'Successfully updated {count} tasks'
                    })
                
                elif operation == 'move_to_list':
                    if not new_list_id:
                        return JsonResponse({
                            'success': False,
                            'error': 'No list specified'
                        }, status=400)
                        
                    try:
                        new_list = BoardList.objects.get(id=new_list_id)
                        # 验证所有任务都属于同一个看板
                        if any(task.board != new_list.board for task in tasks):
                            return JsonResponse({
                                'success': False,
                                'error': 'All tasks must belong to the same board'
                            }, status=400)
                        
                        count = 0
                        for task in tasks:
                            task.board_list = new_list
                            task.save(update_fields=['board_list', 'updated_at'])
                            count += 1
                        
                        return JsonResponse({
                            'success': True,
                            'message': f'Successfully moved {count} tasks'
                        })
                    except BoardList.DoesNotExist:
                        return JsonResponse({
                            'success': False,
                            'error': 'List not found'
                        }, status=404)
                
                elif operation == 'assign':
                    if not assignee_id:
                        return JsonResponse({
                            'success': False,
                            'error': 'No assignee specified'
                        }, status=400)
                        
                    try:
                        user = User.objects.get(id=assignee_id)
                        count = 0
                        for task in tasks:
                            task.assignees.add(user)
                            count += 1
                        
                        return JsonResponse({
                            'success': True,
                            'message': f'Successfully assigned {count} tasks to {user.get_display_name()}'
                        })
                    except User.DoesNotExist:
                        return JsonResponse({
                            'success': False,
                            'error': 'User not found'
                        }, status=404)
                
                else:
                    return JsonResponse({
                        'success': False,
                        'error': '不支持的操作类型'
                    }, status=400)
                    
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    def has_task_edit_access(self, task, user):
        """检查用户是否有任务编辑权限"""
        # 任务创建者
        if task.creator == user:
            return True
        
        # 看板创建者
        board = task.board
        if board.owner == user:
            return True
            
        # 团队管理员
        if board.team:
            team_membership = board.team.memberships.filter(user=user, role__in=['admin', 'owner'], status='active').first()
            if team_membership:
                return True
        
        # 看板管理员
        board_membership = board.members.filter(user=user, role='admin', is_active=True).first()
        if board_membership:
            return True
            
        return False
