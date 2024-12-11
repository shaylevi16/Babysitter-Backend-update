from django.urls import include, path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView
from django.conf import settings
from django.conf.urls.static import static
from base import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# add the full crud's paths
router.register(r'availability', views.AvailableTimeActions, basename='availability')
# router.register(r'babysitters-admin', views.AdminForBabysitter, basename='babysitter-admin')
router.register(r'reviews', views.ReviewsViewSet, basename='reviews')


urlpatterns = [
    path('', views.index),
    # path('availability/', views.TheAvailability),
    path('login/',TokenObtainPairView.as_view()),
    path('register/', views.register),
    path('', include(router.urls)),  
    path('babysitters-list/', views.BabysitterListView.as_view()), # parents view the babysitter list
    path('babysitter-profile/<int:pk>/', views.BabysitterActions.as_view()), # see the babysitter info and update the info
    path('delete-user/', views.deactivate_my_user) , # is active=false on user
    path('parents-list/' , views.ParentsListView.as_view()) , # babysitters view the parents list
    path('parents-profile/<int:pk>/' , views.ParentsActions.as_view()) , # see the parents info and update the info
    path('kids/', views.KidsViewSet.as_view()), # kids view 
    path('Edit-kids/<int:pk>/', views.KidsActions.as_view()), # edit kids 
    path('babysitter-availability/', views.AvailableTimeListView.as_view()), # will be used for parents to see the babysitters availability
    path('create-request/', views.RequestsViewSet.as_view()), # will be used to create request
    path('show-request/', views.ShowRequestForParents.as_view()), # will be used to create request
    path('update-request/<int:pk>/', views.RequestActions.as_view()), # will be used for approve/decline
    path('show-reviews/', views.show_reviews.as_view()), # will be used to show reviews on certain babysitter 

]
    

    

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
