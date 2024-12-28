from django.urls import include, path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView
from django.conf import settings
from django.conf.urls.static import static
from base import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'availability', views.AvailableTimeActions, basename='availability')
router.register(r'reviews', views.ReviewsViewSet, basename='reviews')
router.register(r'babysitters-admin', views.AdminForBabysitter, basename='babysitter-admin')

urlpatterns = [
    # General
    path('', views.index),
    # User
    path('login/',TokenObtainPairView.as_view()),
    path('register/', views.register),
    path('user-delete/', views.deactivate_my_user),
    # Babysitter 
    path('babysitters-list/', views.BabysitterListView.as_view()),
    path('babysitter-profile/<int:pk>/', views.BabysitterActions.as_view()),
    # Parents
    path('parents-list/' , views.ParentsListView.as_view()),
    path('parents-profile/<int:pk>/' , views.ParentsActions.as_view()),
    # Kids
    path('kids-list/', views.KidsListView.as_view()),
    path('kids-add/', views.KidsCreate.as_view()),
    path('kids-update/<int:pk>/', views.KidsActions.as_view()),
    # Available Time
    path('availability-list/', views.AvailableTimeListView.as_view()),
    # + availability/* CRUD (in the router)
    # Requests
    path('request-add/', views.RequestsViewSet.as_view()),
    path('requests-list/', views.ShowRequests.as_view()),
    path('request-update/<int:pk>/', views.RequestActionsForBabysitter.as_view()),
    path('request-delete/<int:pk>/', views.RequestDeactivate.as_view()),
    # Reviews
    path('reviews-list/', views.ShowReviews.as_view()),
    # + reviews/* CRUD (in the router)
    # Meetings
    path('meetings-add/', views.CreateMeetingView.as_view()),
    path('meetings-list/', views.ShowMeetings.as_view()),
    path('meeting-update/<int:pk>/', views.MeetingActionsForBabysitter.as_view()),
    path('meeting-availablity/', views.show_babysitter_availability_for_meetings),
    # Router
    path('', include(router.urls)),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)