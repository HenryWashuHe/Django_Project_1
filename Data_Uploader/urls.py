from django.urls import path, include
from Data_Uploader import views
urlpatterns = [
    path('Upload', views.get_upload_page, name='get_upload_page'),
]

