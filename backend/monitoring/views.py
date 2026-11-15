from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Post, PostAnalysis
from .serializers import PostAnalysisSerializer, PostSerializer


@api_view(['GET'])
def health(request):
    return Response({'status': 'ok'})


class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer


class PostAnalysisListCreateView(generics.ListCreateAPIView):
    queryset = PostAnalysis.objects.all()
    serializer_class = PostAnalysisSerializer
