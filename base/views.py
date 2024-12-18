from django.http import HttpResponse
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import permissions , viewsets , generics, exceptions, status
from .serializer import *
from .models import Babysitter, Meetings, Requests, Parents, Kids, Reviews, AvailableTime
from .permissions import IsParent, IsBabysitter, check_parent_approved_by_babysitter

# ============================================
#                General Pages
# ============================================

def index(req):
    return HttpResponse("hello world")

# ============================================
#                   CRUD
# ============================================

## ===== Users =====

@api_view(['POST'])
def register(request):
    
    """
    Handle user registration for Babysitter/Parent roles.
    """

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

@api_view(['POST'])
def deactivate_my_user(request):
    """
    Deactivate the currently logged-in user.
    Sets 'is_active' to False.
    """
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

## ===== Babysitter =====

class BabysitterListView(generics.ListAPIView):
    """
    Retrieve and display a list of all babysitters.

    This view is used by parents.
    """
    queryset = Babysitter.objects.filter(user__is_active=True)
    serializer_class = BabysitterSerializerForParents
    permission_classes = [IsParent]

class BabysitterActions(generics.RetrieveUpdateAPIView):
    """
    API view for babysitters to retrieve or update their profile.
    """
    queryset = Babysitter.objects.all()
    serializer_class = BabysitterSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Filter the user
    def get_queryset(self):
        return Babysitter.objects.filter(user=self.request.user)
   
    # Update the user with patch
    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

## ===== Parents =====

class ParentsListView(generics.ListAPIView):
    """
    Retrieve and display a list of all parents.

    This view is used by babysitters.
    """
    queryset = Parents.objects.all()
    serializer_class = ParentsSerializerForBabysitter
    permission_classes = [IsBabysitter]

class ParentsActions(generics.RetrieveUpdateAPIView):
    """
    API view for parents to retrieve or update their profile.
    """
    queryset = Parents.objects.all()
    serializer_class = ParentsSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Filter the user
    def get_queryset(self):
        return Parents.objects.filter(user=self.request.user)
    
    # Update the user with patch
    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

## ===== Kids =====

class KidsListView(generics.ListAPIView):
    """
    Retrieve and display a list of kids for a given parent id.
    - **parent_id** (int): The id of the parent.

    This view is used by babysitters.    
    """
    queryset = Kids.objects.all()
    serializer_class = KidsSerializer
    permission_classes = [IsBabysitter]

    def get_queryset(self):
        try:
            parent_id = self.request.data.get('parent_id', None)
            parent=Parents.objects.get(family_id=parent_id)
        except Parents.DoesNotExist:
            raise exceptions.PermissionDenied ("Parent not found")
        return Kids.objects.filter(family=parent)

class KidsCreate(generics.CreateAPIView):
    """
    Allows authenticated parents to add a child to their profile.
    
    Fields required for creating a kid:
    - **name** (str): The name of the kid.
    - **age** (int): The age of the kid.
    - (The `family` field is automatically associated with the currently logged-in parent.)
    """
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
    """
    Get kid info for the given kid id.
    
    Perform the update only if the logged-in user is the parent associated with the kid.
    """
    queryset = Kids.objects.all()
    serializer_class = KidsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        kid = self.get_object()
        parent = kid.family        
        if parent.user != self.request.user:
            raise exceptions.PermissionDenied("You do not have permission to update this kid.")

        serializer.save()

## ===== Available Time =====

class AvailableTimeListView(generics.ListAPIView):
    """
    Retrieve and a list of all available time slots for a given babysitter id.
    - **babysitter_id** (int): The id of the babysitter.

    This view is used by parents. 
    """
    queryset = AvailableTime.objects.all()
    serializer_class = AvailableTimeSerializer
    permission_classes = [IsParent]

    def get_queryset(self):
        try:
            babysitter_id = self.request.data.get('babysitter_id', None)
            if babysitter_id is None:
                raise exceptions.PermissionDenied("You must enter babysitter id")
            
            babysitter=Babysitter.objects.get(id=babysitter_id)
        except Babysitter.DoesNotExist:
            raise exceptions.PermissionDenied ("Babysitter not found")
        
        parents = Parents.objects.get(user=self.request.user)
        if not check_parent_approved_by_babysitter(babysitter, parents):
            return Response({"detail": "Parent not approved by babysitter!"}, status=status.HTTP_404_NOT_FOUND)

        return AvailableTime.objects.filter(babysitter=babysitter)

class AvailableTimeActions(viewsets.ModelViewSet):
    """
    Manage the available time slots for the logged-in babysitter.

    Allows viewing, adding, editing, or removing time slots for the babysitter's availability.
    """
    queryset = AvailableTime.objects.all()
    serializer_class = AvailableTimeSerializer
    permission_classes = [IsBabysitter]

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

## ===== Requests =====

class RequestsViewSet(generics.CreateAPIView):
    """
    Allows authenticated parents to add a request.
    
    Fields required for creating a kid:
    - **babysitter_id** (int): The id of the babysitter.
    - (The `family` field is automatically associated with the currently logged-in parent.)
    """
    queryset = Requests.objects.all()
    serializer_class = RequestsSerializer
    permission_classes = [IsParent]

    def create(self, request):
        try:
            parents = Parents.objects.get(user=request.user)
            babysitter_id = request.data.get('babysitter_id', None)
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
                {"detail":"Request already exists."}, status=status.HTTP_409_CONFLICT)
        
        # Create the Request and associate it with the parent
        request = Requests.objects.create(
            family = parents, 
            babysitter=babysitter
        )
        request.save()
        return Response({"detail":"Request created successfully"} ,
                        status=status.HTTP_201_CREATED)

class ShowRequests(generics.ListAPIView):
    """
    Show all requests info created by the logged-in parent / sent to the logged-in babysitter.    
    """
    queryset = Requests.objects.all()
    serializer_class = RequestsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # depends user type
        if hasattr(self.request.user, 'Parent'):
            return Requests.objects.filter(family=Parents.objects.get(user=self.request.user))
        else:
            return Requests.objects.filter(babysitter=Babysitter.objects.get(user=self.request.user))

class RequestActionsForBabysitter(generics.RetrieveUpdateAPIView):
    """
    Allows authenticated babysitters to get/edit request status of the requests sent to them.
    """
    queryset = Requests.objects.all()
    serializer_class = RequestsStatusSerializer
    permission_classes = [IsBabysitter]

    def get_object(self):
        obj = super().get_object()
        # Ensure the logged-in babysitter is the same as the babysitter in the request
        if obj.babysitter.user != self.request.user:
            raise exceptions.PermissionDenied("You are not authorized to update this request.")
        return obj

## ===== Reviews =====

class ReviewsViewSet(viewsets.ModelViewSet):
    """
    Manage the reviews created by the logged-in parent.

    Allows parents to viewing, adding, editing, or removing their own reviews.
    """
    queryset =Reviews.objects.all()
    serializer_class = ReviewsSerializer
    permission_classes = [IsParent]

    def create(self , request):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            parents = Parents.objects.get(user=request.user)
            babysitter_id = request.data.get('babysitter_id', None)
            if babysitter_id is None:
                raise exceptions.PermissionDenied("You must enter babysitter id")            
            babysitter=Babysitter.objects.get(id=babysitter_id)
        except Babysitter.DoesNotExist:
            return Response(
                {"detail": "Babysitter does not exist."},
                status=status.HTTP_404_NOT_FOUND)
        
        if not check_parent_approved_by_babysitter(babysitter, parents):
            return Response({"detail": "Parent not approved by babysitter!"}, status=status.HTTP_404_NOT_FOUND)    

        reviews = Reviews.objects.create(family = parents , 
                                         babysitter= babysitter ,
                                         review_text=serializer.validated_data.get('review_text') ,
                                         rating=serializer.validated_data.get('rating')  )

        reviews.save()
        return Response({"detail":"Review created successfully"} ,
                            status=status.HTTP_201_CREATED)
    
    def get_object(self):
        instance = super().get_object()
        if instance.family.user != self.request.user:
            raise exceptions.PermissionDenied( "You do not have permission to update this availability.")
        return instance 
    
class ShowReviews(generics.ListAPIView):
    """
    Retrieve a list of all reviews for a given babysitter id.
    - **babysitter_id** (int): The id of the babysitter.

    This view is used by both parents and babysitters. 
    """
    queryset = Reviews.objects.all()
    serializer_class = ReviewsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        id = self.request.data.get('babysitter_id', None)
        if id is None:
            raise exceptions.PermissionDenied("You must enter babysitter id")
        return Reviews.objects.filter(babysitter__id=id)

## ===== Meetings =====

class CreateMeetingView(generics.CreateAPIView):
    """
    Allows a parent to create a meeting with a babysitter based on the available time.
    Fields required for creating a meeting:
    - **start_time** (str): The start time (in datetime format).
    - **end_time** (str): The age of the (in datetime format).
    - **baby_sitter** (int): The babysitter id.
    - (The `family` field is automatically associated with the currently logged-in parent.)
    """
    queryset = Meetings.objects.all()
    serializer_class = MeetingsSerializerForCreating
    permission_classes = [IsParent]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        # Check start and end time inputs
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        parents = Parents.objects.get(user=request.user)

        # Check babysitter validity
        try:        
            babysitter_id = self.request.data.get('babysitter_id', None)
            if babysitter_id is None:
                return Response({"detail": "babysitter_id is required."}, status=status.HTTP_404_NOT_FOUND)
            babysitter = Babysitter.objects.get(id=babysitter_id)
        except Babysitter.DoesNotExist:
            return Response({"detail": "Babysitter does not exist."}, status=status.HTTP_404_NOT_FOUND)
        
        if not check_parent_approved_by_babysitter(babysitter, parents):
            return Response({"detail": "Parent not approved by babysitter!"}, status=status.HTTP_404_NOT_FOUND)

        start_time = serializer.validated_data['start_time']
        end_time = serializer.validated_data['end_time']

        # Check if babysitter is available at the given meeting time
        available_time = AvailableTime.objects.filter(
            babysitter=babysitter,
            date=start_time.date(),
            start_time__lte=start_time.time(),
            end_time__gte=end_time.time()
        ).exists()
        if not available_time:
            return Response({"message": "Babysitter is not available at the requested time."},
                            status=status.HTTP_400_BAD_REQUEST) 

        # Check for existing meeting during the requested time period
        conflicting_meeting = Meetings.objects.filter(
            babysitter=babysitter,
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exists()
        if conflicting_meeting:
            return Response({"message": "Babysitter is busy during the requested time."},
                            status=status.HTTP_400_BAD_REQUEST) 
        
        # Create & Save the new meeting
        meeting = Meetings(
            babysitter=babysitter,
            family=parents,
            start_time=start_time,
            end_time=end_time
        )    
        meeting.save()

        return Response({"message": "Meeting created successfully"}, status=status.HTTP_201_CREATED)

class ShowMeetingsPerBabysitter(generics.ListAPIView):
    """
    Retrieve a list of all meetings for a given babysitter id.
    - **babysitter_id** (int): The id of the babysitter.

    This view is used by both parents and babysitters. 
    """
    queryset = Reviews.objects.all()
    serializer_class = MeetingsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        id = self.request.data.get('babysitter_id', None)
        if id is None:
            raise exceptions.PermissionDenied("You must enter babysitter id")
        return Meetings.objects.filter(babysitter__id=id)
    
class ShowMeetingsForParent(generics.ListAPIView):
    """
    Show all meetings created by the logged-in parent.    
    This view is used by parents.    
    """
    queryset = Meetings.objects.all()
    serializer_class = MeetingsSerializer
    permission_classes = [IsParent]

    def get_queryset(self):
        parents = Parents.objects.get(user=self.request.user)
        return Meetings.objects.filter(family=parents)

## ===== Admin =====

class AdminForBabysitter(viewsets.ModelViewSet):
    queryset = Babysitter.objects.all()
    serializer_class = BabysitterSerializer
    permission_classes = [permissions.IsAdminUser]  # Only admin users can access