from rest_framework import viewsets, status
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .serializers import UserSerializer, UserRegisterSerializer, ProjectSerializer, TaskSerializer, CommentSerializer
from .models import Project, Task, Comment

User = get_user_model()

class UserViewSet(viewsets.ViewSet):
    
    queryset = User.objects.all()

    @extend_schema(responses=UserSerializer)
    def list(self, request):
        serializer = UserSerializer(self.queryset, many=True)
        return Response(serializer.data)

    @extend_schema(request=UserRegisterSerializer, responses=UserSerializer)
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(responses=UserSerializer)
    def retrieve(self, request, pk=None):
        try:
            user = User.objects.get(pk=pk)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        

    @extend_schema(request=UserSerializer, responses=UserSerializer)
    def update(self, request, pk=None):
        try:
            user = User.objects.get(pk=pk)
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
      
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(responses=None)
    def destroy(self, request, pk=None):
        try:
            user = User.objects.get(pk=pk)
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
       

class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    
    @extend_schema(request=UserSerializer, responses=UserSerializer)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class ProjectViewSet(viewsets.ViewSet):
    
    queryset = Project.objects.all()
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=ProjectSerializer)
    def list(self, request):
        serializer = ProjectSerializer(self.queryset, many=True)
        return Response(serializer.data)

    @extend_schema(responses=ProjectSerializer)
    def retrieve(self, request, pk=None):
        try:
            project = Project.objects.get(pk=pk)
            serializer = ProjectSerializer(project)
            return Response(serializer.data)
        except Project.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        

    @extend_schema(request=ProjectSerializer, responses=ProjectSerializer)
    def create(self, request):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request=ProjectSerializer, responses=ProjectSerializer)
    def update(self, request, pk=None):
        try:
            project = Project.objects.get(pk=pk)
            serializer = ProjectSerializer(project, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
        except Project.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(responses=None)
    def destroy(self, request, pk=None):
        try:
            project = Project.objects.get(pk=pk)
            project.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Project.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
class TaskViewSet(viewsets.ViewSet):
    queryset = Task.objects.all()

    @extend_schema(
        parameters=[
            OpenApiParameter(name='project_id', required=False, type=int)
        ],
        responses=TaskSerializer(many=True)
    )
    def list(self, request):
        project_id = request.query_params.get('project_id')
        if project_id is not None:
            tasks = self.queryset.filter(project_id=project_id)
        else:
            tasks = self.queryset.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    @extend_schema(responses=TaskSerializer)
    def retrieve(self, request, pk=None):
        try:
            task = self.queryset.get(pk=pk)
            serializer = TaskSerializer(task)
            return Response(serializer.data)
        except Task.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @extend_schema(request=TaskSerializer, responses=TaskSerializer)
    def create(self, request, project_id=None):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            if project_id:
                try:
                    project = Project.objects.get(pk=project_id)
                    serializer.save(project=project)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                except project.DoesNotExist:
                    return Response({"error": "Project does not exist."}, status=status.HTTP_404_NOT_FOUND)
            else:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request=TaskSerializer, responses=TaskSerializer)
    def update(self, request, pk=None):
        try:
            task = self.queryset.get(pk=pk)
            serializer = TaskSerializer(task, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
        except task.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(responses=None)
    def destroy(self, request, pk=None):
        try:
            task = self.queryset.get(pk=pk)
            task.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except task.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        
class CommentViewSet(viewsets.ViewSet):
    queryset = Comment.objects.all()
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name='task_id', required=False, type=int)
        ],
        responses=CommentSerializer(many=True)
    )
    def list(self, request):
        task_id = request.query_params.get('task_id')
        if task_id is not None:
            comments = self.queryset.filter(task_id=task_id)
        else:
            comments = self.queryset.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    @extend_schema(responses=CommentSerializer)
    def retrieve(self, request, pk=None):
        try:
            comment = self.queryset.get(pk=pk)
            serializer = CommentSerializer(comment)
            return Response(serializer.data)
        except Comment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
    @extend_schema(request=CommentSerializer, responses=CommentSerializer)
    def create(self, request, task_id=None):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            if task_id:
                try:
                    task = Task.objects.get(pk=task_id)
                    serializer.save(task=task)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                except Task.DoesNotExist:
                    return Response({"error": "Task does not exist."}, status=status.HTTP_404_NOT_FOUND)
            else:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(request=CommentSerializer, responses=CommentSerializer)
    def update(self, request, pk=None):
        try:
            comment = self.queryset.get(pk=pk)
            serializer = CommentSerializer(comment, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
        except Comment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(responses=None)
    def destroy(self, request, pk=None):
        try:
            comment = self.queryset.get(pk=pk)
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Comment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)