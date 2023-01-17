from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Room, Topic, Message
from .forms import RoomForm, UserForm
from django.db.models import Q

# Create your views here.


def home(request):
    q = request.GET.get('q')
    # print(q)
    topics = Topic.objects.all()
    rooms = Room.objects.all()
    msgs = Message.objects.all()  # ordering set in Message class in models using Meta dunctionality

    if q != None:
        rooms = Room.objects.filter(Q(topic__name__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q))
        msgs = Message.objects.filter(Q(room__topic__name__icontains=q))

    room_count = rooms.count()
    context = {'rooms' : rooms, 'topics' : topics, 'room_count' : room_count, 'all_messages' : msgs}
    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)

    if request.method == 'POST':
        body = request.POST.get('body')
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = body
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    room_messages = room.message_set.all().order_by('-created')  # Django feature for Many-to-one relationship Model(start in lower case) name_set 
    participants = room.participants.all()

    context = {'room' : room, 'room_messages' : room_messages, 'participants' : participants}
    return render(request, 'base/room.html', context)

@login_required(login_url='login')
def createRoom(request):
    topics=Topic.objects.all()
    form = RoomForm()

    if request.method == 'POST':
        # form = RoomForm(request.POST)
        # if form.is_valid():
        #     room = form.save(commit=False)
        #     room.host = request.user
        #     room.save()
        #     return redirect('home')
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description')
        )
        return redirect('home')
    
    context = {'form':form, 'topics':topics}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def editRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics=Topic.objects.all()

    if request.user != room.host:
        return HttpResponse('You are not the host of this page')

    if request.method == 'POST':
        # form = RoomForm(request.POST, instance=room)
        # if form.is_valid():
        #     form.save()
        #     return redirect('home')
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        room.topic = topic
        room.name = request.POST.get('name')
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')


    context = {'form':form, 'topics':topics, 'room':room}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('You are not the host of this page')

    if request.method == 'POST':
        room.delete()
        return redirect('home')

    context = {'obj' : room}
    return render(request, 'base/delete.html', context)



def loginPage(request):

    if request.user.is_authenticated:
        return redirect('home')

    page = 'login'

    if request.POST:
        username=request.POST.get('username')
        password=request.POST.get('password')
        # print(username)
        try:
            User.objects.get(username=username)
        except:
            messages.error(request, 'Invalid User')
            # return render('login')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')

        else:
            messages.error(request,  'Username or Password does not exist')


    context = {'page' : page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    page = 'register'
    form = UserCreationForm()
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        
        if form.is_valid():
            user = form.save(commit=False)
            # Do some processing with user like checking if username exists, convert to lower, etc.
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "An error occured in registration")

    context = {'form' : form}
    return render(request, 'base/login_register.html', context)


@login_required(login_url='login')
def deleteMessage(request, pk):
    msg = Message.objects.get(id=pk)
    room_id = msg.room.id
    msg.delete()
    return redirect('room', room_id)



def userProfile(request, pk):
    user = User.objects.get(id=pk)

    q = request.GET.get('q')
    
    topics = Topic.objects.all()
    rooms = Room.objects.all()
    msgs = Message.objects.all()  # ordering set in Message class in models using Meta dunctionality

    if q != None:
        rooms = Room.objects.filter(Q(topic__name__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q))
        msgs = Message.objects.filter(Q(room__topic__name__icontains=q))

    room_count = rooms.count()
    context = {'user' : user, 'rooms' : rooms, 'topics' : topics, 'room_count' : room_count, 'all_messages' : msgs}
    return render(request, 'base/profile.html', context)


@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    context = {'form':form}
    return render(request, 'base/update-user.html', context)


def topicsPage(request):
    context = {}
    return render(request, 'base/topics.html', context)