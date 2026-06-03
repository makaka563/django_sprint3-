from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CommentForm, PostForm, UserForm
from .models import Category, Comment, Post


POSTS_PER_PAGE = 10
User = get_user_model()


def get_published_posts():
    return Post.objects.select_related(
        'author',
        'category',
        'location',
    ).filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now(),
    ).annotate(
        comment_count=Count('comments')
    ).order_by(
        '-pub_date'
    )


def paginate(request, post_list):
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    post_list = get_published_posts()
    context = {
        'page_obj': paginate(request, post_list),
    }
    return render(request, 'blog/index.html', context)


def post_detail(request, id):
    post_filter = Q(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now(),
    )
    if request.user.is_authenticated:
        post_filter |= Q(author=request.user)
    post_list = Post.objects.select_related(
        'author',
        'category',
        'location',
    ).filter(post_filter)
    post = get_object_or_404(post_list, pk=id)
    comments = post.comments.select_related('author')
    context = {
        'post': post,
        'form': CommentForm(),
        'comments': comments,
    }
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True,
    )
    post_list = get_published_posts().filter(category=category)
    context = {
        'category': category,
        'page_obj': paginate(request, post_list),
    }
    return render(request, 'blog/category.html', context)


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    if request.user == profile_user:
        post_list = Post.objects.select_related(
            'author',
            'category',
            'location',
        ).filter(
            author=profile_user,
        ).annotate(
            comment_count=Count('comments')
        ).order_by(
            '-pub_date'
        )
    else:
        post_list = get_published_posts().filter(author=profile_user)
    context = {
        'profile': profile_user,
        'page_obj': paginate(request, post_list),
    }
    return render(request, 'blog/profile.html', context)


@login_required
def edit_profile(request):
    form = UserForm(request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/user.html', {'form': form})


@login_required
def create_post(request):
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', id=post.id)


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('blog:post_detail', id=post.id)
    form = PostForm(
        request.POST or None,
        request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', id=post.id)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('blog:post_detail', id=post.id)
    form = PostForm(instance=post)
    if request.method == 'POST':
        username = request.user.username
        post.delete()
        return redirect('blog:profile', username=username)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    if comment.author != request.user:
        return redirect('blog:post_detail', id=comment.post_id)
    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', id=comment.post_id)
    context = {
        'comment': comment,
        'form': form,
    }
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    if comment.author != request.user:
        return redirect('blog:post_detail', id=comment.post_id)
    post_id = comment.post_id
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', id=post_id)
    return render(request, 'blog/comment.html', {'comment': comment})
