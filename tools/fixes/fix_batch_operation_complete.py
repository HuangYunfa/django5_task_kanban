#!/usr/bin/env python3
"""
完全重新创建 TaskBatchOperationView
"""

CORRECT_BATCH_OPERATION_VIEW = '''
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
                operation = data.get('action') or data.get('operation')
            else:
                # 处理表单数据
                task_ids = request.POST.getlist('task_ids')
                operation = request.POST.get('action') or request.POST.get('operation')
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
                        'error': f'No permission to edit task {task_id}'
                    }, status=403)
                tasks.append(task)
            except Task.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': f'Task {task_id} not found'
                }, status=404)
        
        # 执行批量操作
        try:
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
                    if request.content_type == 'application/json':
                        new_status = data.get('new_status')
                    else:
                        new_status = request.POST.get('new_status')
                    
                    if new_status not in dict(Task.STATUS_CHOICES):
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
                    if request.content_type == 'application/json':
                        new_priority = data.get('new_priority')
                    else:
                        new_priority = request.POST.get('new_priority')
                        
                    if new_priority not in dict(Task.PRIORITY_CHOICES):
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
                
                elif operation == 'assign':
                    if request.content_type == 'application/json':
                        assignee_id = data.get('assignee_id')
                    else:
                        assignee_id = request.POST.get('assignee_id')
                    
                    if assignee_id:
                        try:
                            assignee = User.objects.get(id=assignee_id)
                        except User.DoesNotExist:
                            return JsonResponse({
                                'success': False,
                                'error': 'Assignee not found'
                            }, status=404)
                    else:
                        assignee = None
                    
                    count = 0
                    for task in tasks:
                        if assignee:
                            task.assignees.add(assignee)
                        else:
                            task.assignees.clear()
                        count += 1
                    
                    return JsonResponse({
                        'success': True,
                        'message': f'Successfully assigned {count} tasks'
                    })
                
                elif operation == 'move_to_list':
                    if request.content_type == 'application/json':
                        new_list_id = data.get('new_list_id')
                    else:
                        new_list_id = request.POST.get('new_list_id')
                    
                    if not new_list_id:
                        return JsonResponse({
                            'success': False,
                            'error': 'No target list specified'
                        }, status=400)
                    
                    try:
                        new_list = BoardList.objects.get(id=new_list_id)
                    except BoardList.DoesNotExist:
                        return JsonResponse({
                            'success': False,
                            'error': 'Target list not found'
                        }, status=404)
                    
                    # 验证所有任务都属于同一个看板
                    board = tasks[0].board
                    if not all(task.board == board for task in tasks):
                        return JsonResponse({
                            'success': False,
                            'error': 'All tasks must belong to the same board'
                        }, status=400)
                    
                    # 验证目标列表属于同一个看板  
                    if new_list.board != board:
                        return JsonResponse({
                            'success': False,
                            'error': 'Target list must belong to the same board'
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
                
                else:
                    return JsonResponse({
                        'success': False,
                        'error': f'Unknown operation: {operation}'
                    }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    def has_task_edit_access(self, task, user):
        """检查用户是否有编辑任务的权限"""
        # 任务创建者
        if task.creator == user:
            return True
        
        # 任务被分配人
        if task.assignees.filter(id=user.id).exists():
            return True
            
        # 看板所有者
        if task.board.owner == user:
            return True
        
        # 看板管理员
        board_membership = task.board.members.filter(user=user, role='admin', is_active=True).first()
        if board_membership:
            return True
            
        return False

'''


def fix_batch_operation_view():
    """修复批量操作视图"""
    views_path = "taskkanban/tasks/views.py"
    
    # 读取文件内容
    with open(views_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到 TaskBatchOperationView 类的开始和结束位置
    start_marker = "class TaskBatchOperationView(LoginRequiredMixin, View):"
    end_marker = "class TaskSortView(LoginRequiredMixin, View):"
    
    start_pos = content.find(start_marker)
    end_pos = content.find(end_marker)
    
    if start_pos == -1 or end_pos == -1:
        print("无法找到TaskBatchOperationView类的位置")
        return False
    
    # 替换内容
    before = content[:start_pos]
    after = content[end_pos:]
    new_content = before + CORRECT_BATCH_OPERATION_VIEW.strip() + "\n\n\n" + after
    
    # 写入修复后的内容
    with open(views_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"已修复 TaskBatchOperationView 类: {views_path}")
    return True


if __name__ == "__main__":
    fix_batch_operation_view()
