from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.urls import reverse
import logging
from .models import Category, Post, AboutUs
from django.core.paginator import Paginator
from .forms import ContactForm, ForgotPassword, NewPostForm, RegisterForm, LoginForm, ResetPassword
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
# Create your views here.

# posts = [{'id': 1, 'title': 'Post 1', 'content': 'This is post 1', 'game': 'Foortball'},
#         {'id': 2, 'title': 'Post 2', 'content': 'This is post 2', 'game': 'Cricket'},
#         {'id': 3, 'title': 'Post 3', 'content': 'This is post 3', 'game': 'Chess'},
#         {'id': 4, 'title': 'Post 4', 'content': 'This is post 4', 'game': 'Hockey'},
#         ]

def index(request):
    name = "Latest"
    all_posts = Post.objects.filter(is_published = True)

    #Paginate
    paginator = Paginator(all_posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'index.html', {'Name': name, 'page_obj': page_obj})


def details(request, slug):
    if request.user and not request.user.has_perm('blog.view_post'):
        messages.error(request=request, message="You don't have permission to view")
        return redirect('blog:index')
    post = Post.objects.get(slug=slug)
    related_post = Post.objects.filter(category = post.category).exclude(id = post.id)
    if not related_post:
        related_post.title = "No related posts"
        related_post.url = ""
        print(related_post)
    #Static data
    # post = next((item for item in posts if item['id'] == int(post_id)), None)
    # logger = logging.getLogger("Test")
    # logger.debug("error"+post)
    # logger.debug("error"+Post)
    return render(request, "detail.html", {'post' : post, 'related_posts': related_post})

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        # form.cleaned_data['name']
        logger = logging.getLogger("Test")
        if form.is_valid():
            logger.debug(f"DATA {form.cleaned_data['name']} {form.cleaned_data['email']} {form.cleaned_data['message']}")
            success_message = "Your request is submitted"
            return render(request, "contact.html", {'form': form, 'success': success_message})
        # else:
        #     logger.debug("Invalid Form")
        return render(request, "contact.html", {'form': form, 'name': name, 'email': email, 'message': message})
    return render(request, "contact.html")

def about(request):
    about_content = AboutUs.objects.first()
    # print(about_content)
    if about_content is None or not about_content.content:
        about_content = "This is default message"
    else:
        about_content = about_content.content
    return render(request, "about.html", {'about_content': about_content})
# def old_url(request):
#     return redirect(reverse("blog:new_url"))


# def new_url_redirect(request):
#     return HttpResponse("New url")
def register(request):
    form = RegisterForm()
    if request.method == 'POST':
        form  = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit = False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            readers_group, created = Group.objects.get_or_create(name="Readers")
            user.groups.add(readers_group)
            messages.success(request, "Registration successful!")
            return redirect("/login")
    return render(request, 'register.html', {'form': form})

def login(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password = password)
            print("user")
            if user is not None:
                auth_login(request, user)
                print("success")
                return redirect("/dashboard")
    return render(request, 'login.html', {'form': form})

def dashboard(request):
    blog_title = "My blog"
    all_posts = Post.objects.filter(user = request.user)
    paginator = Paginator(all_posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "dashboard.html", {'blog_title': blog_title, 'page_obj': page_obj})

def logout_user(request):
    logout(request)
    return redirect('blog:index')

def forgot_password(request):
    form = ForgotPassword()
    if request.method == 'POST':
        form = ForgotPassword(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            current_site = get_current_site(request)
            subject = "Reset Password"
            domain = current_site.domain
            message = render_to_string('reset_password_mail.html',{
                "domain": domain,
                'uid': uid,
                'token': token
            })
            send_mail(subject=subject, message=message, from_email='noreply@test.com', recipient_list=[email])
            messages.success(request, 'Email has been sent')

    return render(request, 'forgot_password.html', {'form': form})

def reset_password(request, uidb64, token):
    form = ResetPassword()
    if request.method == 'POST':
        form = ResetPassword(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            try:
                uid = urlsafe_base64_decode(uidb64)
                user = User.objects.get(pk = uid)
            except(TypeError, ValueError, User.DoesNotExist, OverflowError):
                user = None
            if user is not None and default_token_generator.check_token(user, token):
                user.set_password(new_password)
                user.save()
                messages.success(request=request, message="Your Password has been reset successfully")
                return redirect('blog:login')
            else:
                messages.error(request, 'The reset link is invalid')
    return render(request, 'reset_password.html', {'form': form})

@login_required
def new_post(request):
    categories = Category.objects.all()
    form = NewPostForm()
    if request.method == 'POST':
        form = NewPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('blog:dashboard')
    return render(request, 'new_post.html', {'categories': categories, 'form': form})

def edit_post(request, post_id):
    categories = Category.objects.all()
    post = get_object_or_404(Post, id= post_id)

    if request.method == 'POST':
        form = NewPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post.save()
            return redirect('blog:dashboard')
    return render(request, 'edit_post.html',{'categories': categories, 'post': post})

def delete_post(request, post_id):
    post = get_object_or_404(Post, id = post_id)
    post.delete()
    messages.success(request=request, message="Post deleted successfully")
    return redirect('blog:dashboard')

def publish_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.is_published = True
    post.save()
    messages.success(request=request, message="Post published successfully")
    return redirect("blog:dashboard")