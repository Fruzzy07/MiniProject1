from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required


def home(request):
    posts = Post.objects.all()
    return render(request, 'home.html', {'posts': posts})


def post_list(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'blog/post_list.html', {'posts': posts})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.all()
    comment_form = CommentForm()  # Instantiate the form here
    if request.user.is_authenticated:
        # Allow comments to be added
        return render(request, 'blog/post_detail.html', {'post': post, 'comments': comments, 'form': comment_form})
    else:
        # User is not authenticated, show message
        error_message = "You must be logged in to add a comment."
        return render(request, 'blog/post_detail.html', {
            'post': post,
            'comments': comments,
            'form': comment_form,
            'error_message': error_message
        })



def create_post(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to create a post.")
        return redirect('login')

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)  # Include request.FILES
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_form.html', {'form': form})



def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.user != post.author:
        messages.error(request, "You do not have permission to edit it")
        return redirect('post_detail', pk=post.pk)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)  # Добавьте request.FILES здесь
        if form.is_valid():
            form.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_form.html', {'form': form})


def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.user != post.author:
        messages.error(request, "You do not have permission to delete it")
        return redirect('post_detail', pk=post.pk)

    if request.method == 'POST':
        post.delete()
        return redirect('home')  # Redirect to home or any other page after deletion
    return render(request, 'blog/post_confirm_delete.html', {'post': post})
@login_required  # Ensure that only authenticated users can add comments
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user  # This will only work if the user is authenticated
            comment.post = post
            comment.save()
            return redirect('post_detail', pk=post.pk)

    return render(request, 'blog/post_detail.html', {'post': post, 'form': form})

