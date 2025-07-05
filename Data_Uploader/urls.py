from django.urls import path, include
import Data_Uploader.views
urlpatterns=[
    path('Upload',Data_Uploader.views.get_upload_page)
]

