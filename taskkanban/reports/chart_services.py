"""
Reports应用数据服务 - Chart模块
处理图表数据格式化和转换
"""
import json
from django.utils import timezone
from datetime import datetime, timedelta
import random


class ChartDataService:
    """图表数据服务类，用于处理Chart.js数据格式转换"""
    
    # 图表颜色配置
    CHART_COLORS = [
        '#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b', 
        '#6f42c1', '#fd7e14', '#20c997', '#6c757d', '#17a2b8'
    ]
    
    @staticmethod
    def format_for_chartjs(data, chart_type, options=None):
        """
        将数据格式化为Chart.js所需格式
        
        Args:
            data: 要转换的数据
            chart_type: 图表类型 (line, bar, pie, doughnut)
            options: 额外配置选项
            
        Returns:
            dict: Chart.js格式的数据
        """
        if not data:
            return {}
            
        options = options or {}
        
        # 根据图表类型选择格式化方法
        if chart_type == 'line':
            return ChartDataService.format_line_chart(data, options)
        elif chart_type == 'bar':
            return ChartDataService.format_bar_chart(data, options)
        elif chart_type in ['pie', 'doughnut']:
            return ChartDataService.format_pie_chart(data, options)
        else:
            raise ValueError(f"不支持的图表类型: {chart_type}")
    
    @staticmethod
    def format_line_chart(data, options=None):
        """
        格式化折线图数据
        
        Args:
            data: 包含日期和值的数据列表
            options: 额外配置选项
            
        Returns:
            dict: 格式化后的Chart.js数据
        """
        options = options or {}
        
        # 检查数据格式
        if not isinstance(data, list):
            return {}
            
        if not data:
            return {
                'labels': [],
                'datasets': []
            }
            
        # 确定标签和数据字段
        if 'date' in data[0]:
            # 日期时间序列数据
            date_field = 'date'
        elif 'label' in data[0]:
            # 已有标签的数据
            date_field = 'label'
        else:
            # 尝试找到第一个可用作标签的字段
            date_field = list(data[0].keys())[0]
        
        # 提取所有标签
        labels = [item[date_field] for item in data]
        
        # 确定数据字段(除了日期/标签字段)
        value_fields = [k for k in data[0].keys() if k != date_field]
        
        # 为每个数据字段创建数据集
        datasets = []
        for i, field in enumerate(value_fields):
            # 使用循环颜色
            color_index = i % len(ChartDataService.CHART_COLORS)
            color = ChartDataService.CHART_COLORS[color_index]
            
            dataset = {
                'label': options.get(f'{field}_label', field.replace('_', ' ').title()),
                'data': [item.get(field, 0) for item in data],
                'backgroundColor': options.get(f'{field}_background', color),
                'borderColor': options.get(f'{field}_border', color),
                'tension': options.get('tension', 0.4),
                'fill': options.get('fill', False),
            }
            datasets.append(dataset)
        
        return {
            'labels': labels,
            'datasets': datasets
        }
    
    @staticmethod
    def format_bar_chart(data, options=None):
        """
        格式化柱状图数据
        
        Args:
            data: 包含标签和值的数据列表
            options: 额外配置选项
            
        Returns:
            dict: 格式化后的Chart.js数据
        """
        options = options or {}
        
        # 检查数据格式
        if not isinstance(data, list) or not data:
            return {
                'labels': [],
                'datasets': []
            }
        
        # 确定标签和值字段
        label_field = next((f for f in ['label', 'name', 'category'] if f in data[0]), None)
        value_field = next((f for f in ['value', 'count', 'total'] if f in data[0]), None)
        
        if not label_field or not value_field:
            # 如果没有标准字段，使用第一个和第二个字段
            fields = list(data[0].keys())
            if len(fields) < 2:
                return {'labels': [], 'datasets': []}
            
            label_field = fields[0]
            value_field = fields[1]
        
        # 提取标签和值
        labels = [str(item[label_field]) for item in data]
        values = [item[value_field] for item in data]
        
        # 生成背景颜色
        if options.get('use_different_colors', True):
            # 每个柱子使用不同颜色
            background_colors = [
                ChartDataService.CHART_COLORS[i % len(ChartDataService.CHART_COLORS)]
                for i in range(len(values))
            ]
        else:
            # 所有柱子使用相同颜色
            background_colors = options.get('background_color', ChartDataService.CHART_COLORS[0])
        
        return {
            'labels': labels,
            'datasets': [{
                'label': options.get('dataset_label', '数值'),
                'data': values,
                'backgroundColor': background_colors,
                'borderColor': options.get('border_color', 'rgba(0, 0, 0, 0.1)'),
                'borderWidth': options.get('border_width', 1)
            }]
        }
    
    @staticmethod
    def format_pie_chart(data, options=None):
        """
        格式化饼图/环形图数据
        
        Args:
            data: 包含标签和值的数据列表
            options: 额外配置选项
            
        Returns:
            dict: 格式化后的Chart.js数据
        """
        options = options or {}
        
        # 检查数据格式
        if not isinstance(data, list) or not data:
            return {
                'labels': [],
                'datasets': []
            }
        
        # 确定标签和值字段
        label_field = next((f for f in ['label', 'name', 'category'] if f in data[0]), None)
        value_field = next((f for f in ['value', 'count', 'total'] if f in data[0]), None)
        
        if not label_field or not value_field:
            # 如果没有标准字段，使用第一个和第二个字段
            fields = list(data[0].keys())
            if len(fields) < 2:
                return {'labels': [], 'datasets': []}
            
            label_field = fields[0]
            value_field = fields[1]
        
        # 提取标签和值
        labels = [str(item[label_field]) for item in data]
        values = [item[value_field] for item in data]
        
        # 生成背景颜色
        background_colors = [
            ChartDataService.CHART_COLORS[i % len(ChartDataService.CHART_COLORS)]
            for i in range(len(values))
        ]
        
        return {
            'labels': labels,
            'datasets': [{
                'data': values,
                'backgroundColor': background_colors,
                'borderColor': options.get('border_color', '#ffffff'),
                'borderWidth': options.get('border_width', 1)
            }]
        }
    
    @staticmethod
    def get_demo_chart_data(chart_type, data_type=None):
        """
        生成演示图表数据
        
        Args:
            chart_type: 图表类型 (line, bar, pie, doughnut)
            data_type: 数据类型 (daily, category, etc.)
            
        Returns:
            dict: 格式化后的Chart.js数据
        """
        if chart_type == 'line':
            # 生成最近30天的日期
            dates = [(timezone.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(29, -1, -1)]
            
            # 根据数据类型生成不同的演示数据
            if data_type == 'task_completion':
                # 任务完成趋势
                data = [
                    {
                        'date': date,
                        'completed': random.randint(1, 15),
                        'created': random.randint(3, 20)
                    }
                    for date in dates
                ]
                return ChartDataService.format_line_chart(data)
                
            elif data_type == 'workload':
                # 工作负载趋势
                data = [
                    {
                        'date': date,
                        'assigned': random.randint(5, 30),
                        'completed': random.randint(1, 20)
                    }
                    for date in dates
                ]
                return ChartDataService.format_line_chart(data)
            
            else:
                # 默认趋势数据
                data = [
                    {
                        'date': date,
                        'value': random.randint(10, 100)
                    }
                    for date in dates
                ]
                return ChartDataService.format_line_chart(data)
                
        elif chart_type == 'bar':
            if data_type == 'user_workload':
                # 用户工作负载
                users = ['张三', '李四', '王五', '赵六', '钱七', '孙八', '周九', '吴十']
                data = [
                    {
                        'label': user,
                        'value': random.randint(5, 50)
                    }
                    for user in users
                ]
                return ChartDataService.format_bar_chart(data)
                
            elif data_type == 'priority_distribution':
                # 优先级分布
                priorities = ['低优先级', '普通', '高优先级', '紧急']
                data = [
                    {
                        'label': priority,
                        'value': random.randint(5, 50)
                    }
                    for priority in priorities
                ]
                return ChartDataService.format_bar_chart(data)
                
            else:
                # 默认柱状图数据
                categories = ['类别A', '类别B', '类别C', '类别D', '类别E']
                data = [
                    {
                        'label': category,
                        'value': random.randint(10, 100)
                    }
                    for category in categories
                ]
                return ChartDataService.format_bar_chart(data)
                
        elif chart_type in ['pie', 'doughnut']:
            if data_type == 'status_distribution':
                # 状态分布
                statuses = ['待办', '进行中', '审核中', '已完成', '已阻塞']
                data = [
                    {
                        'label': status,
                        'value': random.randint(5, 30)
                    }
                    for status in statuses
                ]
                return ChartDataService.format_pie_chart(data)
                
            elif data_type == 'team_distribution':
                # 团队分布
                teams = ['开发团队', '设计团队', '产品团队', '测试团队', '运维团队']
                data = [
                    {
                        'label': team,
                        'value': random.randint(10, 50)
                    }
                    for team in teams
                ]
                return ChartDataService.format_pie_chart(data)
                
            else:
                # 默认饼图数据
                categories = ['类别A', '类别B', '类别C', '类别D', '类别E']
                data = [
                    {
                        'label': category,
                        'value': random.randint(10, 100)
                    }
                    for category in categories
                ]
                return ChartDataService.format_pie_chart(data)
        
        # 默认返回空数据
        return {
            'labels': [],
            'datasets': []
        }
