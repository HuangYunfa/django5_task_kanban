"""
报表导出服务模块
提供PDF、Excel、CSV等格式的报表导出功能
"""

import os
import csv
import json
from datetime import datetime
from io import BytesIO, StringIO
from typing import Dict, List, Any, Optional

from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class ReportExportService:
    """报表导出服务类"""
    
    def __init__(self, data: Dict[str, Any], report_title: str = "报表"):
        """
        初始化导出服务
        
        Args:
            data: 报表数据
            report_title: 报表标题
        """
        self.data = data
        self.report_title = report_title
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    def export_to_csv(self, filename: Optional[str] = None) -> HttpResponse:
        """导出为CSV格式"""
        if not filename:
            filename = f"{self.report_title}_{self.timestamp}.csv"
        
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # 添加BOM以支持Excel中文显示
        response.write('\ufeff')
        
        writer = csv.writer(response)
        
        # 写入标题
        writer.writerow([f'{self.report_title} - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'])
        writer.writerow([])  # 空行
        
        # 写入摘要数据
        if 'summary' in self.data:
            writer.writerow(['摘要信息'])
            for key, value in self.data['summary'].items():
                writer.writerow([self._translate_key(key), value])
            writer.writerow([])  # 空行
        
        # 写入详细数据
        self._write_detailed_data_to_csv(writer)
        
        return response
    
    def export_to_excel(self, filename: Optional[str] = None) -> HttpResponse:
        """导出为Excel格式"""
        if not PANDAS_AVAILABLE:
            raise ImportError("需要安装pandas库才能导出Excel格式")
        
        if not filename:
            filename = f"{self.report_title}_{self.timestamp}.xlsx"
        
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # 摘要工作表
            if 'summary' in self.data:
                summary_data = []
                for key, value in self.data['summary'].items():
                    summary_data.append({
                        '指标': self._translate_key(key),
                        '数值': value
                    })
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='摘要', index=False)
            
            # 详细数据工作表
            self._write_detailed_data_to_excel(writer)
        
        output.seek(0)
        
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
    
    def export_to_pdf(self, filename: Optional[str] = None) -> HttpResponse:
        """导出为PDF格式"""
        if not REPORTLAB_AVAILABLE:
            raise ImportError("需要安装reportlab库才能导出PDF格式")
        
        if not filename:
            filename = f"{self.report_title}_{self.timestamp}.pdf"
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # 创建PDF文档
        doc = SimpleDocTemplate(response, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # 标题
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=18,
            spaceAfter=20,
            alignment=1  # 居中
        )
        story.append(Paragraph(self.report_title, title_style))
        story.append(Paragraph(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # 摘要信息
        if 'summary' in self.data:
            story.append(Paragraph("摘要信息", styles['Heading2']))
            
            summary_data = [['指标', '数值']]
            for key, value in self.data['summary'].items():
                summary_data.append([self._translate_key(key), str(value)])
            
            summary_table = Table(summary_data)
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(summary_table)
            story.append(Spacer(1, 20))
        
        # 详细数据
        self._write_detailed_data_to_pdf(story, styles)
        
        # 构建PDF
        doc.build(story)
        
        return response
    
    def export_to_json(self, filename: Optional[str] = None) -> HttpResponse:
        """导出为JSON格式"""
        if not filename:
            filename = f"{self.report_title}_{self.timestamp}.json"
        
        response = HttpResponse(content_type='application/json; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        export_data = {
            'title': self.report_title,
            'generated_at': datetime.now().isoformat(),
            'data': self.data
        }
        
        json.dump(export_data, response, ensure_ascii=False, indent=2)
        
        return response
    
    def _write_detailed_data_to_csv(self, writer):
        """写入详细数据到CSV"""
        # 任务统计
        if 'task_stats' in self.data:
            writer.writerow(['任务统计'])
            task_stats = self.data['task_stats']
            
            # 状态统计
            if 'status_stats' in task_stats:
                writer.writerow(['状态', '数量'])
                for stat in task_stats['status_stats']:
                    writer.writerow([stat.get('status', ''), stat.get('count', 0)])
                writer.writerow([])
            
            # 优先级统计
            if 'priority_stats' in task_stats:
                writer.writerow(['优先级', '数量'])
                for stat in task_stats['priority_stats']:
                    writer.writerow([stat.get('priority', ''), stat.get('count', 0)])
                writer.writerow([])
        
        # 用户工作负载
        if 'workload_stats' in self.data and 'user_workloads' in self.data['workload_stats']:
            writer.writerow(['用户工作负载统计'])
            writer.writerow(['用户', '总任务', '已完成', '进行中', '待办', '完成率'])
            for workload in self.data['workload_stats']['user_workloads']:
                writer.writerow([
                    workload.get('display_name', ''),
                    workload.get('total_tasks', 0),
                    workload.get('completed_tasks', 0),
                    workload.get('in_progress_tasks', 0),
                    workload.get('todo_tasks', 0),
                    f"{workload.get('completion_rate', 0):.1f}%"
                ])
            writer.writerow([])
        
        # 团队绩效
        if 'team_stats' in self.data and 'team_stats' in self.data['team_stats']:
            writer.writerow(['团队绩效统计'])
            writer.writerow(['团队', '成员数', '总任务', '已完成', '完成率', '人均任务'])
            for team in self.data['team_stats']['team_stats']:
                writer.writerow([
                    team.get('team_name', ''),
                    team.get('member_count', 0),
                    team.get('total_tasks', 0),
                    team.get('completed_tasks', 0),
                    f"{team.get('completion_rate', 0):.1f}%",
                    f"{team.get('tasks_per_member', 0):.1f}"
                ])
            writer.writerow([])
        
        # 项目进度
        if 'project_stats' in self.data and 'project_stats' in self.data['project_stats']:
            writer.writerow(['项目进度统计'])
            writer.writerow(['项目', '总任务', '已完成', '进行中', '进度', '预计完成'])
            for project in self.data['project_stats']['project_stats']:
                writer.writerow([
                    project.get('board_name', ''),
                    project.get('total_tasks', 0),
                    project.get('completed_tasks', 0),
                    project.get('in_progress_tasks', 0),
                    f"{project.get('progress_rate', 0):.1f}%",
                    project.get('estimated_completion', '未知')
                ])
    
    def _write_detailed_data_to_excel(self, writer):
        """写入详细数据到Excel"""
        # 用户工作负载
        if 'workload_stats' in self.data and 'user_workloads' in self.data['workload_stats']:
            workload_data = []
            for workload in self.data['workload_stats']['user_workloads']:
                workload_data.append({
                    '用户': workload.get('display_name', ''),
                    '总任务': workload.get('total_tasks', 0),
                    '已完成': workload.get('completed_tasks', 0),
                    '进行中': workload.get('in_progress_tasks', 0),
                    '待办': workload.get('todo_tasks', 0),
                    '完成率': f"{workload.get('completion_rate', 0):.1f}%"
                })
            
            if workload_data:
                workload_df = pd.DataFrame(workload_data)
                workload_df.to_excel(writer, sheet_name='用户工作负载', index=False)
        
        # 团队绩效
        if 'team_stats' in self.data and 'team_stats' in self.data['team_stats']:
            team_data = []
            for team in self.data['team_stats']['team_stats']:
                team_data.append({
                    '团队': team.get('team_name', ''),
                    '成员数': team.get('member_count', 0),
                    '总任务': team.get('total_tasks', 0),
                    '已完成': team.get('completed_tasks', 0),
                    '完成率': f"{team.get('completion_rate', 0):.1f}%",
                    '人均任务': f"{team.get('tasks_per_member', 0):.1f}"
                })
            
            if team_data:
                team_df = pd.DataFrame(team_data)
                team_df.to_excel(writer, sheet_name='团队绩效', index=False)
        
        # 项目进度
        if 'project_stats' in self.data and 'project_stats' in self.data['project_stats']:
            project_data = []
            for project in self.data['project_stats']['project_stats']:
                project_data.append({
                    '项目': project.get('board_name', ''),
                    '总任务': project.get('total_tasks', 0),
                    '已完成': project.get('completed_tasks', 0),
                    '进行中': project.get('in_progress_tasks', 0),
                    '进度': f"{project.get('progress_rate', 0):.1f}%",
                    '预计完成': project.get('estimated_completion', '未知')
                })
            
            if project_data:
                project_df = pd.DataFrame(project_data)
                project_df.to_excel(writer, sheet_name='项目进度', index=False)
    
    def _write_detailed_data_to_pdf(self, story, styles):
        """写入详细数据到PDF"""
        # 用户工作负载
        if 'workload_stats' in self.data and 'user_workloads' in self.data['workload_stats']:
            story.append(Paragraph("用户工作负载统计", styles['Heading2']))
            
            workload_data = [['用户', '总任务', '已完成', '进行中', '待办', '完成率']]
            for workload in self.data['workload_stats']['user_workloads']:
                workload_data.append([
                    workload.get('display_name', ''),
                    str(workload.get('total_tasks', 0)),
                    str(workload.get('completed_tasks', 0)),
                    str(workload.get('in_progress_tasks', 0)),
                    str(workload.get('todo_tasks', 0)),
                    f"{workload.get('completion_rate', 0):.1f}%"
                ])
            
            if len(workload_data) > 1:
                workload_table = Table(workload_data)
                workload_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(workload_table)
                story.append(Spacer(1, 20))
        
        # 团队绩效
        if 'team_stats' in self.data and 'team_stats' in self.data['team_stats']:
            story.append(Paragraph("团队绩效统计", styles['Heading2']))
            
            team_data = [['团队', '成员数', '总任务', '已完成', '完成率']]
            for team in self.data['team_stats']['team_stats']:
                team_data.append([
                    team.get('team_name', ''),
                    str(team.get('member_count', 0)),
                    str(team.get('total_tasks', 0)),
                    str(team.get('completed_tasks', 0)),
                    f"{team.get('completion_rate', 0):.1f}%"
                ])
            
            if len(team_data) > 1:
                team_table = Table(team_data)
                team_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(team_table)
                story.append(Spacer(1, 20))
    
    def _translate_key(self, key: str) -> str:
        """翻译键名为中文"""
        translations = {
            'total_tasks': '总任务数',
            'completion_rate': '完成率',
            'active_users': '活跃用户数',
            'active_teams': '活跃团队数',
            'active_projects': '活跃项目数',
            'completed_tasks': '已完成任务',
            'in_progress_tasks': '进行中任务',
            'todo_tasks': '待办任务',
        }
        return translations.get(key, key)


class ChartExportService:
    """图表导出服务类"""
    
    @staticmethod
    def export_chart_data(chart_data: Dict[str, Any], filename: Optional[str] = None) -> HttpResponse:
        """导出图表数据为JSON格式"""
        if not filename:
            filename = f"chart_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        response = HttpResponse(content_type='application/json; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        export_data = {
            'generated_at': datetime.now().isoformat(),
            'chart_data': chart_data
        }
        
        json.dump(export_data, response, ensure_ascii=False, indent=2)
        
        return response
