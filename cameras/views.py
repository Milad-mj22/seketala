from django.shortcuts import render , redirect , get_object_or_404

from cameras.forms import CameraForm
from cameras.models import Camera, DetectedPersons
from users.models import Profile
from django.contrib.auth.models import User
from django.contrib import messages
# Create your views here.


def manage_cameras(request):
    # Display the list of cameras and their configurations
    cameras = Camera.objects.all()
    return render(request, 'cameras/manage_cameras.html', {'cameras': cameras})




def add_camera(request):
    if request.method == 'POST':
        form = CameraForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Camera added successfully.')
            return redirect('manage_cameras')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CameraForm()

    return render(request, 'cameras/add_edit_camera.html', {
        'form': form,
        'action': 'Add' if form.instance._state.adding else 'Edit'
    })


def edit_camera(request, camera_id):
    camera = get_object_or_404(Camera, id=camera_id)
    if request.method == 'POST':
        form = CameraForm(request.POST, instance=camera)
        if form.is_valid():
            form.save()
            messages.success(request, 'Camera updated successfully.')
            return redirect('manage_cameras')
    else:
        form = CameraForm(instance=camera)
    return render(request, 'cameras/add_edit_camera.html', {'form': form, 'action': 'Edit', 'camera': camera})

def delete_camera(request, camera_id):
    camera = get_object_or_404(Camera, id=camera_id)
    camera.delete()
    messages.success(request, 'Camera deleted successfully.')
    return redirect('manage_cameras')







from django.http import JsonResponse
import requests  # Optional: Use for testing camera connection

def check_connectivity(request):
    ip = request.GET.get('ip')
    port = request.GET.get('port')
    username = request.GET.get('username')
    password = request.GET.get('password')

    # Simulate checking camera connectivity (can be done with requests or using a custom camera API)
    try:
        # Sample check for the connection, replace with actual camera check logic
        response = requests.get(f"http://{ip}:{port}/status", auth=(username, password))

        if response.status_code == 200:
            return JsonResponse({
                "status": "connected",
                "live_feed_url": f"http://{ip}:{port}/live"
            })
        else:
            return JsonResponse({"status": "failed"})
    except requests.exceptions.RequestException:
        return JsonResponse({"status": "failed"})



from django.shortcuts import render
from .models import Camera

def live_cameras(request):
    cameras = Camera.objects.filter(is_active=True)
    return render(request, "cameras/live_cameras.html", {"cameras": cameras})




def live_camera(request, camera_id):
    # Display live camera feed based on camera ID
    camera = Camera.objects.get(id=camera_id)
    return render(request, 'cameras/live_camera.html', {'camera': camera})

def detect_person(request):
    # Handle person detection logic here
    detected_persons = Profile.objects.all()  # Example, replace with actual detection
    return render(request, 'cameras/detect_person.html', {'detected_persons': detected_persons})


def assign_person_to_user(request, person_id):
    # Assign detected person to a specific user
    person = DetectedPersons.objects.get(id=person_id)
    if request.method == 'POST':
        user = User.objects.get(id=request.POST['user_id'])
        person.assigned_user = user
        person.save()
        return redirect('dashboard')
    users = User.objects.all()
    return render(request, 'cameras/assign_person_to_user.html', {'person': person, 'users': users})