"""
URL configuration for PaperManager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from rest_framework.routers import DefaultRouter
from PaperSummarizer import views
from django.urls import path, include

router = DefaultRouter()
router.register(r'summaries', views.SummaryViewSet, basename='summary')
router.register(r'labels', views.LabelViewSet, basename='label')
router.register(r'papers', views.PaperViewSet, basename='paper')

urlpatterns = [
    path('', include(router.urls)),
    path('upload/', views.upload_and_extract_text, name='upload_and_extract_text'),
]