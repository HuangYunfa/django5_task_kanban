#!/usr/bin/env python3
"""
任务标签系统实施计划
"""

# 1. 创建标签管理视图
LABEL_MANAGEMENT_VIEWS = """
# 在 boards/views.py 中添加

class BoardLabelCreateView(LoginRequiredMixin, View):
    '''创建看板标签API'''
    
    def post(self, request, slug):
        board = get_object_or_404(Board, slug=slug)
        
        # 权限检查
        if not self.has_board_edit_access(board, request.user):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        try:
            data = json.loads(request.body)
            name = data.get('name', '').strip()
            color = data.get('color', '#61bd4f')
            
            if not name:
                return JsonResponse({'error': 'Label name is required'}, status=400)
            
            # 检查标签是否已存在
            if board.labels.filter(name=name).exists():
                return JsonResponse({'error': 'Label already exists'}, status=400)
            
            # 创建标签
            label = BoardLabel.objects.create(
                board=board,
                name=name,
                color=color
            )
            
            return JsonResponse({
                'success': True,
                'label': {
                    'id': label.id,
                    'name': label.name,
                    'color': label.color
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class BoardLabelListView(LoginRequiredMixin, View):
    '''获取看板标签列表API'''
    
    def get(self, request, slug):
        board = get_object_or_404(Board, slug=slug)
        
        # 权限检查
        if not self.has_board_access(board, request.user):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        labels = board.labels.all().values('id', 'name', 'color')
        
        return JsonResponse({
            'success': True,
            'labels': list(labels)
        })
"""

# 2. 任务标签操作API
TASK_LABEL_OPERATIONS = """
# 在 tasks/views.py 中添加

class TaskLabelUpdateView(LoginRequiredMixin, TaskAccessMixin, View):
    '''任务标签更新API'''
    
    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        
        if not self.has_task_edit_access(task, request.user):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        try:
            data = json.loads(request.body)
            action = data.get('action')  # 'add' or 'remove'
            label_id = data.get('label_id')
            
            if not label_id:
                return JsonResponse({'error': 'Label ID is required'}, status=400)
            
            # 验证标签属于同一看板
            label = get_object_or_404(BoardLabel, id=label_id, board=task.board)
            
            if action == 'add':
                task.labels.add(label)
                message = f'Added label {label.name}'
            elif action == 'remove':
                task.labels.remove(label)
                message = f'Removed label {label.name}'
            else:
                return JsonResponse({'error': 'Invalid action'}, status=400)
            
            return JsonResponse({
                'success': True,
                'message': message,
                'labels': [
                    {'id': l.id, 'name': l.name, 'color': l.color}
                    for l in task.labels.all()
                ]
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
"""

# 3. 前端标签组件
FRONTEND_LABEL_COMPONENTS = """
<!-- 在模板中添加标签显示组件 -->

<!-- 任务卡片中的标签显示 -->
<div class="task-labels">
    {% for label in task.labels.all %}
        <span class="label" style="background-color: {{ label.color }};">
            {{ label.name }}
        </span>
    {% endfor %}
</div>

<!-- 标签选择器 -->
<div class="label-selector">
    <button type="button" class="btn btn-sm btn-outline-secondary" 
            data-bs-toggle="dropdown">
        <i class="fas fa-tag"></i> Labels
    </button>
    <div class="dropdown-menu">
        {% for label in board.labels.all %}
            <div class="dropdown-item">
                <input type="checkbox" 
                       class="label-checkbox" 
                       data-label-id="{{ label.id }}"
                       {% if label in task.labels.all %}checked{% endif %}>
                <span class="label-preview" style="background-color: {{ label.color }};">
                    {{ label.name }}
                </span>
            </div>
        {% endfor %}
        <div class="dropdown-divider"></div>
        <button class="dropdown-item" onclick="createNewLabel()">
            <i class="fas fa-plus"></i> Create new label
        </button>
    </div>
</div>
"""

# 4. JavaScript交互逻辑
JAVASCRIPT_INTERACTIONS = """
// 标签操作JavaScript

// 切换任务标签
function toggleTaskLabel(taskId, labelId, isChecked) {
    const action = isChecked ? 'add' : 'remove';
    
    fetch(`/tasks/${taskId}/labels/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            action: action,
            label_id: labelId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 更新任务卡片中的标签显示
            updateTaskLabels(taskId, data.labels);
            showNotification('success', data.message);
        } else {
            showNotification('error', data.error);
            // 恢复复选框状态
            event.target.checked = !isChecked;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('error', 'Operation failed');
        event.target.checked = !isChecked;
    });
}

// 创建新标签
function createNewLabel() {
    const name = prompt('Enter label name:');
    if (!name) return;
    
    const color = prompt('Enter label color (hex):', '#61bd4f');
    if (!color) return;
    
    fetch(`/boards/${boardSlug}/labels/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            name: name,
            color: color
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 刷新标签列表
            location.reload();
            showNotification('success', 'Label created successfully');
        } else {
            showNotification('error', data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('error', 'Failed to create label');
    });
}

// 更新任务卡片标签显示
function updateTaskLabels(taskId, labels) {
    const taskCard = document.querySelector(`[data-task-id="${taskId}"]`);
    if (!taskCard) return;
    
    const labelsContainer = taskCard.querySelector('.task-labels');
    if (!labelsContainer) return;
    
    labelsContainer.innerHTML = labels.map(label => 
        `<span class="label" style="background-color: ${label.color};">${label.name}</span>`
    ).join('');
}
"""

print("🏷️ 任务标签系统实施计划")
print("=" * 50)
print("1. 后端API开发 (boards/views.py + tasks/views.py)")
print("2. 前端模板组件 (标签显示和选择器)")
print("3. JavaScript交互逻辑 (AJAX操作)")
print("4. URL路由配置")
print("5. CSS样式设计")
print("\n下一步：开始实施第一个组件...")
