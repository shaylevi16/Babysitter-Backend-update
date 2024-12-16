from django.http import HttpResponse
from .serializer import *
from .models import Babysitter, Meetings, Requests, Parents, Kids, Reviews, AvailableTime
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions , viewsets , generics, exceptions, status
from django.contrib.auth.models import User
from .permissions import IsParent , IsBabysitter

# example
def index(req):
    return HttpResponse("hello world")


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer


#i’m protected
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def about(req): 
 return HttpResponse("about")


####  Register ####

@api_view(['POST'])
def register(request):
    # Create the user
    user_serializer = RegistrationSerializer(data=request.data)
    if not user_serializer.is_valid():
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializers_map = {
        'Babysitter': BabysitterSerializer,
        'Parent': ParentsSerializer,    
    }
    user_type = request.data.get('user_type', None)
    profile_serializer_class = serializers_map.get(user_type)
    if profile_serializer_class is None:
        return Response({"error" : "invalid user type"} , status=status.HTTP_400_BAD_REQUEST)

    profile_serializer = profile_serializer_class(data = request.data)
    if not profile_serializer.is_valid():
        return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    user = user_serializer.save()
    profile_serializer.save(user = user)
    return Response({"message" : f"{user_type} User created successfuly"} , status=status.HTTP_201_CREATED)



#### BabySitter ####


# Will be used by parents to view all babysitters
class BabysitterListView(generics.ListAPIView):
    queryset = Babysitter.objects.filter(user__is_active=True)
    serializer_class = BabysitterSerializerForParents
    permission_classes = [IsParent]

# Will be used by logged-in babysitter to view/edit its values
class BabysitterActions(generics.RetrieveUpdateAPIView):
    queryset = Babysitter.objects.all()
    serializer_class = BabysitterSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Filter the user
    def get_queryset(self):
        return Babysitter.objects.filter(user=self.request.user)
   
    # Update the user with patch
    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


# Get id and deactivate the user (is_active=False)
@api_view(['POST'])
def deactivate_my_user(request):
     # Ensure the logged-in user matches the provided user_id
    try:
        # Fetch the user by the ID
        user = User.objects.get(id=request.user.id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # Deactivate the user
    user.is_active = False
    user.save()
    
    return Response({"message": "User account Deleted successfully"}, status=status.HTTP_200_OK)


########################################################################################################

# # Will be used for admin - Later
# class AdminForBabysitter(viewsets.ModelViewSet):
#     queryset = Babysitter.objects.all()
#     serializer_class = BabysitterSerializer
#     permission_classes = [permissions.IsAdminUser]  # Only admin users can access



#### Parent ####


# Will be used by babysitters to view all parents
class ParentsListView(generics.ListAPIView):
    queryset = Parents.objects.all()
    serializer_class = ParentsSerializerForBabysitter
    permission_classes = [IsBabysitter]

# Will be used by logged-in parents to view/edit its values
class ParentsActions(generics.RetrieveUpdateAPIView):
    queryset = Parents.objects.all()
    serializer_class = ParentsSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Filter the user
    def get_queryset(self):
        return Parents.objects.filter(user=self.request.user)
    
    # Update the user with patch
    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


#### Kids ####


# create+read+update
# Kids crud
class KidsViewSet(generics.CreateAPIView):
    queryset = Kids.objects.all()
    serializer_class = KidsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            family = Parents.objects.get(user=request.user)
        except Parents.DoesNotExist:
            return Response(
                {"detail": "Family (parent) does not exist."},
                status=status.HTTP_404_NOT_FOUND)
        
        # Create the Kids and associate it with the parent
        kid = Kids.objects.create(
            family = family, 
            name=serializer.validated_data.get('name'),
            age=serializer.validated_data.get('age')
        )
        kid.save()
        return Response(self.get_serializer(kid).data,status=status.HTTP_201_CREATED)
    
class KidsActions(generics.RetrieveUpdateAPIView):
    queryset = Kids.objects.all()
    serializer_class = KidsSerializer
    permission_classes = [permissions.IsAuthenticated]
    # Update the kids with patch
    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
    


#### Available Time ####


# create+read+update+delete
# Availability crud
class AvailableTimeActions(viewsets.ModelViewSet):
    queryset =AvailableTime.objects.all()
    serializer_class = AvailableTimeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            babysitter = Babysitter.objects.get(user=request.user)
        except Babysitter.DoesNotExist:
            return Response(
                {"detail": "Babysitter does not exist."},
                status=status.HTTP_404_NOT_FOUND)
        
        # Create the availability time
        available_time = AvailableTime.objects.create( 
            babysitter = babysitter, 
            date = serializer.validated_data.get('date') , 
            start_time = serializer.validated_data.get('start_time'), 
            end_time = serializer.validated_data.get('end_time')
        )
        available_time.save()
        return Response(self.get_serializer(available_time).data,status=status.HTTP_201_CREATED)
    
    def get_queryset(self):
        return AvailableTime.objects.filter(babysitter__user=self.request.user)
    
    # Update the available time with patch
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Check babysitter's authentication
        if instance.babysitter.user != request.user:
            return Response(
                {"detail": "You do not have permission to update this availability."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Handle partial updates
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
        
    def perform_destroy(self, instance):
            instance.delete()

# Will be used by Parents to view all babysitter's availability
class AvailableTimeListView(generics.ListAPIView):
        queryset = AvailableTime.objects.all()
        serializer_class = AvailableTimeSerializer
        permission_classes = [IsParent]

   

#### Requests ####

# create+read
class RequestsViewSet(generics.CreateAPIView):
    queryset = Requests.objects.all()
    serializer_class = RequestsSerializer
    permission_classes = [IsParent]

    def create(self, request):
        try:
            parents = Parents.objects.get(user=request.user)
            babysitter_id = request.data.get('id', None)
            babysitter=Babysitter.objects.get(id=babysitter_id)
        except Parents.DoesNotExist:
            return Response(
                {"detail": "Family (parent) does not exist."},
                status=status.HTTP_404_NOT_FOUND)
        except Babysitter.DoesNotExist:
            return Response(
                {"detail": "Babysitter does not exist."},
                status=status.HTTP_404_NOT_FOUND)
        if Requests.objects.filter(family = parents, babysitter=babysitter).exists():
            return Response(
                {"detail":"request already exists."}, status=status.HTTP_409_CONFLICT)
        
        # Create the Kids and associate it with the parent
        request = Requests.objects.create(
            family = parents, 
            babysitter=babysitter
        )
        request.save()
        return Response({"detail":"Request sent successfully"} ,
                        status=status.HTTP_201_CREATED)

# For parents
class ShowRequestForParents(generics.ListAPIView):
    queryset = Requests.objects.all()
    serializer_class = RequestsSerializer
    permission_classes = [IsParent]

    def get_queryset(self):
        return Requests.objects.filter(family=Parents.objects.get(user=self.request.user))


# For babysitter 
class RequestActions(generics.RetrieveUpdateAPIView):
    queryset = Requests.objects.all()
    serializer_class = RequestsStatusSerializer
    permission_classes = [IsBabysitter]

    # Filter the user
    
   


# id = models.AutoField(primary_key=True)
#     family = models.ForeignKey(Parents, related_name='requests',  on_delete=models.CASCADE)
#     babysitter = models.ForeignKey(Babysitter, related_name='requests', on_delete=models.CASCADE)
#     status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)




#### Meetings ####


# create+read
# Info crud
class MeetingsViewSet(viewsets.ModelViewSet):
    queryset = Meetings.objects.all()
    serializer_class = MeetingsSerializer
    permission_classes = [permissions.IsAuthenticated]



#### Reviews ####


# create+read
# Reviews crud
# For Parents
class ReviewsViewSet(viewsets.ModelViewSet):
    queryset =Reviews.objects.all()
    serializer_class = ReviewsSerializer
    permission_classes = [IsParent]

    def create(self , request):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            parents = Parents.objects.get(user=request.user)
            babysitter_id = request.data.get('id', None)
            babysitter=Babysitter.objects.get(id=babysitter_id)
        except Babysitter.DoesNotExist:
            return Response(
                {"detail": "Babysitter does not exist."},
                status=status.HTTP_404_NOT_FOUND)

        reviews = Reviews.objects.create(family = parents , 
                                         babysitter= babysitter ,
                                         review_text=serializer.validated_data.get('review_text') ,
                                         rating=serializer.validated_data.get('rating')  )

        reviews.save()
        return Response({"detail":"Request sent successfully"} ,
                            status=status.HTTP_201_CREATED)
    
    def get_object(self):
        instance = super().get_object()
        if instance.family.user != self.request.user:
            raise exceptions.PermissionDenied( "You do not have permission to update this availability.")
        return instance 
    


# show thr Reviews for everyone
class show_reviews(generics.ListAPIView):
    queryset = Reviews.objects.all()
    serializer_class = ReviewsSerializer
    permission_classes = [permissions.IsAuthenticated]


    def get_queryset(self):
        id = self.request.data.get('babysitter_id', None)
        if id is None:
            raise exceptions.PermissionDenied ("You must enter Babisitter id")
        return Reviews.objects.filter(babysitter__id=id)
    


 
        
    

    

   
    











