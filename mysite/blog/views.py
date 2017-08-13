from django.shortcuts import render,get_object_or_404,redirect
from django.utils import timezone
from blog.models import Post,Comment
from django.contrib.auth.models import User
from blog.forms import PostForm,CommentForm,RegistrationForm
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (TemplateView,ListView,
DetailView,CreateView,UpdateView,DeleteView)
# from django.contrib.auth import authenticate,login,logout
# Create your views here.

class AboutView(TemplateView):
    template_name = 'about.html'

class PostListView(ListView):
    model = Post

    def get_queryset(self):
        return Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')

class PostDetailView(DetailView):
    model = Post


class CreatePostView(LoginRequiredMixin,CreateView):

    login_url = '/login/'
    redirect_field_name = 'blog/post_detail.html'
    template_name = 'post_form.html'
    form_class = PostForm
    model = Post

    # def form_valid(self, form):
    #     form.instance.user = self.request.user
    #     return super(CreatePostView, self).form_valid(form)
    def form_valid(self, form):
        if(self.request.method=="POST"):
            candidate = form.save(commit=False)
            candidate.author = User.objects.get(username=self.request.user)  # use your own profile here
            candidate.save()
        # return HttpResponseRedirect(self.get_success_url())
        return super(CreatePostView, self).form_valid(form)
    # def form_valid(self, form):
    #     obj = form.save(commit=False)
    #     obj.created_by = self.request.user
    #     obj.save()
    #     return HttpResponseRedirect(self.get_success_url())


class PostUpdateView(LoginRequiredMixin,UpdateView):
    login_url = '/login/'
    redirect_field_name = 'blog/post_detail.html'
    form_class = PostForm
    model = Post

class PostDeleteView(LoginRequiredMixin,DeleteView):
        model = Post
        success_url = reverse_lazy('post_list')

class DraftListView(LoginRequiredMixin,ListView):
    login_url = '/login/'
    redirect_field_name = 'blog/post_list.html'

    model = Post

    def get_queryset(self):
        return Post.objects.filter(published_date__isnull=True).order_by('created_date')

######################################################

@login_required
def post_publish(request,pk):
    post = get_object_or_404(Post,pk=pk)
    post.publish()
    return redirect('post_detail',pk=post.pk)


def add_comment_to_post(request,pk):
    post = get_object_or_404(Post,pk=pk)
    if(request.method =="POST"):
        form = CommentForm(request.POST)
        if(form.is_valid()):
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('post_detail',pk=post.pk)
    else:
        form = CommentForm
    return render(request,'blog/comment_form.html',{'form':form})

@login_required
def comment_approve(request,pk):
    comment = get_object_or_404(Comment,pk=pk)
    comment.approve()
    return redirect('post_detail',pk=comment.post.pk)

@login_required
def comment_remove(request,pk):
    comment = get_object_or_404(Comment,pk=pk)
    post_pk = comment.post.pk
    comment.delete()
    return redirect('post_detail',pk=post_pk)

def register(request):
    registered = False

    if(request.method =="POST"):
        user_form = RegistrationForm(data=request.POST)

        if(user_form.is_valid()):
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            registered = True
        else:
            print(user_form.errors)

    else:
        user_form = RegistrationForm

    return render(request,'blog/registration.html',
    {'user_form':user_form,'registered':registered})
