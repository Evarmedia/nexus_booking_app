from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, update_session_auth_hash, get_user_model
from django.contrib.auth.forms import PasswordResetForm,PasswordChangeForm
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm, SlotForm
from .serializers import UserRegistrationSerializer, UserLoginSerializer
from django.contrib.auth.tokens import default_token_generator
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .models import Slot, Hairstylist, Booking
from django.utils.crypto import get_random_string
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from .serializers import HairstylistSerializer
from .serializers import SlotSerializer
from django.contrib.auth.forms import PasswordChangeForm










User = get_user_model()


# User Registration for Web
def user_registration(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()

            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(str(user.pk).encode())  
            activate_url = f'http://127.0.0.1:8000/accounts/confirm-email/{uid}/{token}/'

            context = {
                'user': user,
                'activate_url': activate_url
            }
            email_body = render_to_string('email_confirmation.html', context)

            send_mail(
                'Confirm Your Email Address',
                email_body,  
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
                html_message=email_body  
            )

            messages.success(request, "Account created. Please check your email to confirm.")
            return redirect('login')
        else:
            messages.error(request, "There was an error with your registration.")
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})



# User Login for Web
def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('available_slots')  
            else:
                messages.error(request, "Invalid credentials.")
        else:
            messages.error(request, "Invalid form input.")
    else:
        form = UserLoginForm()

    return render(request, 'login.html', {'form': form})


def password_reset(request):
    return auth_views.PasswordResetView.as_view()(request)

def confirm_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_object_or_404(User, pk=uid)

        if default_token_generator.check_token(user, token):
            user.is_active = True  
            user.save()
            return JsonResponse({"message": "Email confirmed successfully!"}, status=200)
        else:
            return JsonResponse({"error": "Invalid token"}, status=400)

    except (ValueError, TypeError, OverflowError, User.DoesNotExist):
        return JsonResponse({"error": "Invalid user or token"}, status=400)





def add_hairstylist(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        email = request.POST.get('email')

        # Check if user already exists
        user, created = User.objects.get_or_create(username=email, defaults={"email": email})

        if not created:
            messages.error(request, "A user with this email already exists!")
            return redirect("add_hairstylist")  

        # Generate a temporary password
        temp_password = get_random_string(length=8)
        user.set_password(temp_password)
        user.save()

        # Create the hairstylist profile
        hairstylist = Hairstylist.objects.create(email=email, name=name, description=description, requires_password_reset=True)

        # Send login details via email
        subject = "Your Hairstylist Account Details"
        message = (
            f"Dear {name},\n\n"
            f"You have been added as a hairstylist on our platform.\n\n"
            f"Login details:\n"
            f"Email: {email}\n"
            f"Temporary Password: {temp_password}\n\n"
            f"Please log in and change your password immediately.\n"
            f"Login here: http://127.0.0.1:8000/hairstylist-login/"
        )

        send_mail(subject, message, settings.EMAIL_HOST_USER, [email], fail_silently=False)

        messages.success(request, "Hairstylist added. Login details sent via email.")
        return redirect('add-slot')  

    return render(request, 'add_hairstylist.html')


def hairstylist_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)
        if user and hasattr(user, 'hairstylist'):
            login(request, user)

            if user.hairstylist.requires_password_reset:
                return redirect("hairstylist_change_password")

            return redirect("add_slot")

        messages.error(request, "Invalid login credentials")
    
    return render(request, "hairstylist_login.html")

@login_required
def create_booking(request, slot_id):
    slot = get_object_or_404(Slot, id=slot_id)

    if slot.available:
        booking = Booking.objects.create(user=request.user, slot=slot)
        booking.send_confirmation_email()

        slot.available = False  
        slot.save()

        return redirect('available_slots')  
    else:
        return JsonResponse({"error": "Slot is not available"}, status=400)
    


@login_required
def available_slots(request):
    if hasattr(request.user, 'hairstylist'):
        slots = Slot.objects.filter(hairstylist=request.user.hairstylist)
    else:
        slots = Slot.objects.filter(available=True)  

    return render(request, 'available_slots.html', {'slots': slots})

@login_required
def add_slot(request):
    try:
        hairstylist = request.user.hairstylist
    except Hairstylist.DoesNotExist:
        return redirect('some_error_page') 

    if request.method == "POST":
        form = SlotForm(request.POST)
        if form.is_valid():
            slot = form.save(commit=False)
            slot.hairstylist = hairstylist 
            slot.save()
            return redirect('available_slots')  

    else:
        form = SlotForm()
    
    return render(request, 'add_slots.html', {'form': form})


@login_required
def delete_slot(request, slot_id):
    slot = get_object_or_404(Slot, id=slot_id)

    if request.user.hairstylist != slot.hairstylist:
        return JsonResponse({"error": "Unauthorized"}, status=403)  

    slot.delete()
    return redirect('available_slots')

@login_required
def edit_slot(request, slot_id):
    slot = get_object_or_404(Slot, id=slot_id)

    if request.user.hairstylist != slot.hairstylist:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    if request.method == "POST":
        form = SlotForm(request.POST, instance=slot)
        if form.is_valid():
            form.save()
            return redirect('available_slots')  
    else:
        form = SlotForm(instance=slot)

    return render(request, 'edit_slot.html', {'form': form, 'slot': slot})



@login_required
def hairstylist_change_password(request):
    if not hasattr(request.user, 'hairstylist'):
        return redirect('login')

    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  
            user.hairstylist.requires_password_reset = False
            user.hairstylist.save()
            return redirect('add_slot')

    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'hairstylist_change_password.html', {'form': form})






# User Registration API
class UserRegistrationAPI(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            confirmation_url = f'http://127.0.0.1:8000/accounts/confirm-email/{user.id}/'
            send_mail(
                'Confirm Your Email',
                f'Click here to confirm your email: {confirmation_url}',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            return Response({"message": "Account created. Please check your email to confirm."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# User Login API
class UserLoginAPI(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return Response({"message": "Login successful."}, status=status.HTTP_200_OK)
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Password Reset API
class PasswordResetAPI(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        form = PasswordResetForm({'email': email})
        if form.is_valid():
            form.save(
                email_template_name='password_reset_email.html', 
                subject_template_name='password_reset_subject.txt',
                use_https=request.is_secure(),
                request=request,
            )
            return Response({"message": "Password reset email sent."}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid email."}, status=status.HTTP_400_BAD_REQUEST)



class AddHairstylistAPI(APIView):
    def post(self, request, *args, **kwargs):
        name = request.data.get('name')
        description = request.data.get('description')
        email = request.data.get('email')

        if not name or not email:
            return Response({"error": "Name and email are required."}, status=status.HTTP_400_BAD_REQUEST)

        temp_password = get_random_string(length=8)

        user = User.objects.create_user(username=email, email=email, password=temp_password)

        hairstylist = Hairstylist.objects.create(
            user=user, 
            name=name, 
            description=description, 
            requires_password_reset=True
        )

        subject = "Your Hairstylist Account Details"
        message = (
            f"Dear {name},\n\n"
            f"You have been added as a hairstylist on our platform.\n\n"
            f"Login details:\n"
            f"Email: {email}\n"
            f"Temporary Password: {temp_password}\n\n"
            f"Please log in and change your password immediately.\n"
            f"Login here: http://127.0.0.1:8000/hairstylist-login/"
        )

        send_mail(subject, message, settings.EMAIL_HOST_USER, [email], fail_silently=False)

        return Response({"message": "Hairstylist added successfully."}, status=status.HTTP_201_CREATED)
    



class HairstylistLoginAPI(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(request, username=email, password=password)

        if user and hasattr(user, 'hairstylist'):
            login(request, user)

            token, _ = Token.objects.get_or_create(user=user)

            if user.hairstylist.requires_password_reset:
                return Response({"message": "Password reset required.", "reset_required": True}, status=status.HTTP_403_FORBIDDEN)

            return Response({"message": "Login successful.", "token": token.key}, status=status.HTTP_200_OK)

        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)


class CreateBookingAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slot_id, *args, **kwargs):
        slot = get_object_or_404(Slot, id=slot_id)

        if not slot.available:
            return Response({"error": "Slot is not available"}, status=status.HTTP_400_BAD_REQUEST)

        booking = Booking.objects.create(user=request.user, slot=slot)
        booking.send_confirmation_email()

        slot.available = False
        slot.save()

        return Response({"message": "Booking successful."}, status=status.HTTP_201_CREATED)
    

class AvailableSlotsAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if hasattr(request.user, 'hairstylist'):
            slots = Slot.objects.filter(hairstylist=request.user.hairstylist)
        else:
            slots = Slot.objects.filter(available=True)

        serializer = SlotSerializer(slots, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class AddSlotAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            hairstylist = request.user.hairstylist
        except Hairstylist.DoesNotExist:
            return Response({"error": "Only hairstylists can add slots."}, status=status.HTTP_403_FORBIDDEN)

        serializer = SlotSerializer(data=request.data)
        if serializer.is_valid():
            slot = serializer.save(hairstylist=hairstylist)
            return Response({"message": "Slot added successfully."}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class EditSlotAPI(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, slot_id, *args, **kwargs):
        slot = get_object_or_404(Slot, id=slot_id)

        if request.user.hairstylist != slot.hairstylist:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        serializer = SlotSerializer(slot, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Slot updated successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteSlotAPI(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, slot_id, *args, **kwargs):
        slot = get_object_or_404(Slot, id=slot_id)

        if request.user.hairstylist != slot.hairstylist:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        slot.delete()
        return Response({"message": "Slot deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class HairstylistChangePasswordAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        form = PasswordChangeForm(request.user, request.data)

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            user.hairstylist.requires_password_reset = False
            user.hairstylist.save()

            return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)

        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
    


class ConfirmEmailAPI(APIView):
    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = get_object_or_404(User, pk=uid)

            if default_token_generator.check_token(user, token):
                user.is_active = True
                user.save()
                return Response({"message": "Email confirmed successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

        except (ValueError, TypeError, OverflowError, User.DoesNotExist):
            return Response({"error": "Invalid user or token"}, status=status.HTTP_400_BAD_REQUEST)
