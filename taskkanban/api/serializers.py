from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field

from tasks.models import Task
from boards.models import Board, BoardList, BoardMember
from teams.models import Team, TeamMembership
from reports.models import Report

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'is_active']
        read_only_fields = ['id', 'date_joined', 'is_active']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password_confirm']
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("密码不匹配")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class BoardListSerializer(serializers.ModelSerializer):
    task_count = serializers.SerializerMethodField()
    
    class Meta:
        model = BoardList
        fields = ['id', 'name', 'position', 'task_count']
    
    @extend_schema_field(serializers.IntegerField)
    def get_task_count(self, obj):
        return obj.tasks.count()


class TaskSerializer(serializers.ModelSerializer):
    assignees = UserSerializer(many=True, read_only=True)
    creator = UserSerializer(read_only=True)
    
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'priority', 'board', 'board_list', 'creator', 'assignees', 'due_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'creator', 'created_at', 'updated_at']


class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'priority', 'board', 'board_list', 'assignees', 'due_date']


class BoardSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    boardlist_set = BoardListSerializer(many=True, read_only=True)
    task_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Board
        fields = ['id', 'name', 'description', 'visibility', 'owner', 'boardlist_set', 'task_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']
    
    @extend_schema_field(serializers.IntegerField)
    def get_task_count(self, obj):
        return obj.tasks.count()


class BoardCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ['name', 'description', 'visibility', 'template']


class TeamMembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = TeamMembership
        fields = ['id', 'user', 'role', 'joined_at', 'status']


class TeamSerializer(serializers.ModelSerializer):
    memberships = TeamMembershipSerializer(many=True, read_only=True)
    member_count = serializers.SerializerMethodField()
    board_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Team
        fields = ['id', 'name', 'description', 'avatar', 'is_public', 'allow_join_request', 'memberships', 'member_count', 'board_count', 'created_by', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    @extend_schema_field(serializers.IntegerField)
    def get_member_count(self, obj):
        return obj.teammembership_set.filter(status='active').count()
    
    @extend_schema_field(serializers.IntegerField)
    def get_board_count(self, obj):
        return obj.boards.count()


class TeamCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['name', 'description', 'avatar', 'is_public', 'allow_join_request']


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['id', 'name', 'description', 'report_type', 'config', 'is_public', 'created_by', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'
