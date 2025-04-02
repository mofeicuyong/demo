from django.urls import path
from .views import RegisterView, LoginView, UserProfileView,PredictAPIView,TrainAPIView
from hello.views import hello_page
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('predict/', PredictAPIView.as_view(),name="predict"),
    path('train/', TrainAPIView.as_view(),name="train")
]
