from django.db.models.aggregates import Sum
from rest_framework import generics, views, parsers, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from os.path import join, exists
from pathlib import Path

from .filters import FileFilter, FolderFilter
from .models import File, Folder, Comment
from .serializers import FileListSerializer, FileDetailSerializer, FolderSerializer, CommentSerializer

# print('\n\n\n\n', file_path, '\n\n\n\n')

# Create your views here.
"""
Notes:
istifadecinin users fieldden cixaranda hemcinin stared_usersden de cixar
"""


class FileListAV(generics.ListCreateAPIView):
    queryset = File.objects.all()
    serializer_class = FileListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = FileFilter
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]


    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.serializer_class(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def create(self, request):
        request.data['folder'] = request.data['folder'] if request.data['folder'] != 'null' else None
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class FileDetailAV(generics.RetrieveUpdateDestroyAPIView):
    queryset=File.objects.all()
    serializer_class = FileDetailSerializer

    def destroy(self, *args, **kwargs):
        instance = self.get_object()
        if instance.deleted:
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            instance.deleted = True
            instance.save()
            return Response(data=self.get_serializer(instance=instance).data, status=status.HTTP_202_ACCEPTED)



# class FileUploadView(views.APIView):
#     parser_classes = [parsers.FileUploadParser]

#     def put(self, request, pk, filename):
#         file_data = request.FILES['file']
#         file_instance = File.objects.get(pk=pk)
#         directory = join(
#             str(file_instance.author.id),
#             str(file_instance.folder and file_instance.folder.id)
#         )
#         full_directory = join(settings.MEDIA_ROOT, directory)
#         full_path = join(full_directory, filename)
#         media_inner_path = join(directory, filename)
        
#         Path(full_directory).mkdir(parents=True, exist_ok=True)
#         with open(full_path, mode='wb') as file:
#             for chunk in file_data.chunks():
#                 file.write(chunk)

#         file_instance.file_object.name = media_inner_path
#         file_instance.save()
        
#         return Response(status=204)


def download(request, pk):
    instance = get_object_or_404(File, pk=pk)
    file_path = instance.file_object.path
    # print('\n\n\n\n', file_path, '\n\n\n\n')

    if exists(file_path) and "(instance.author == request.user or request.user in instance.users.all())":
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type=instance.mime_type)
            response['Content-Disposition'] = 'attachment; filename=' + instance.name
            return response
    raise Http404

@api_view(['GET'])
def total_size(request):
    queryset = File.objects.filter(author=request.user)
    result = queryset.aggregate(total_size = Sum('size'))
    return Response(result)

@api_view(['PUT'])
def file_star(request, pk):
    file = get_object_or_404(File, pk=pk)
    should_be_stared = request.data.get('stared')
    if not should_be_stared and file in request.user.stared_files.all():
        file.stared_users.remove(request.user)
    elif should_be_stared:
        file.stared_users.add(request.user)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    file.save()
    serializer = FileDetailSerializer(instance=file, context={'request': request})
    return Response(data=serializer.data ,status=status.HTTP_202_ACCEPTED)


class FolderListAV(generics.ListCreateAPIView):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = FolderFilter

    def create(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

class FolderDetailAV(generics.RetrieveUpdateDestroyAPIView):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer

    def destroy(self, *args, **kwargs):
        instance = self.get_object()
        if instance.deleted:
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            instance.deleted = True
            instance.save()
            return Response(data=self.get_serializer(instance=instance).data, status=status.HTTP_202_ACCEPTED)


class CommentListAV(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

class CommentDetailAV(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer