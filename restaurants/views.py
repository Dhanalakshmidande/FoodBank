from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .forms import RestaurantCreateForm,CartForm
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Restaurant, Comment,Cart,Product
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from paypal.standard.forms import PayPalPaymentsForm
import uuid


class RestaurantListView(ListView):
    queryset = Restaurant.objects.all()
    paginate_by = 6
    template_name = 'restaurants/restaurant_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q')
        cat = self.request.GET.get('cat')
        author = self.request.GET.get('author')
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(details__icontains=q)
            ).distinct()
        if cat:
            queryset = queryset.filter(categories__icontains=cat)
 
        if author:
            queryset = queryset.filter(user__username=author)
        return queryset

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        post_id = request.POST.get('unlike')
        post_id2 = request.POST.get('like')
        if post_id is not None:
            post = get_object_or_404(Restaurant, id=post_id)
            post.likes.remove(request.user)
        if post_id2 is not None:
            post_id2 = request.POST.get('like')
            post = get_object_or_404(Restaurant, id=post_id2)
            post.likes.add(request.user)
        return redirect('home')


class RestaurantDetailView(DetailView):
    queryset = Restaurant.objects.all()

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        comment = request.POST.get('comment')
        c_slug = request.POST.get('slug')
        if comment:
            if c_slug:
                post = get_object_or_404(Restaurant, slug=c_slug)
                comment = Comment.objects.create(
                    user=request.user, post=post, text=comment)
                comment.save()
                return redirect('detail', c_slug)
        return redirect('detail', c_slug)
               

class RestaurantCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    template_name = 'restaurants/restaurant_form.html'
    form_class = RestaurantCreateForm
    success_url = reverse_lazy('my_posts')
    success_message = "Post Created Successfully"

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.user = self.request.user
        return super().form_valid(form)


class RestaurantUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    form_class = RestaurantCreateForm
    template_name = 'restaurants/restaurant_form.html'
    success_url = reverse_lazy('my_posts')
    success_message = "Post Updated Successfully"

    def get_queryset(self):
        return Restaurant.objects.filter(user=self.request.user)


class RestaurantDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    success_url = reverse_lazy('my_posts')
    success_message = "Post Deleted Successfully"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return Restaurant.objects.filter(user=self.request.user)


class MyPostView(LoginRequiredMixin, ListView):
    template_name = 'restaurants/my_posts.html'

    def get_queryset(self):
        return Restaurant.objects.filter(user=self.request.user)

def cart_view(request):
    if request.method == 'POST' and request.POST.get('delete') == 'Delete':
        item_id = request.POST.get('item_id')
        cd=Cart.objects.get(id = item_id)
        cd.delete()
    c = get_cart(request)
    t = total_(request)
    co = item_count(request)
    context = {'c':c ,'t':t }
    return render(request,'cart.html',context)

def checkout(request):
    items=get_cart(request)
    for i in items:
        b = Buy(product_id = i.product_id,quantity=i.quantity,price=i.price)
        b.save()
    
        paypal_dict={
            "business":"sb-viewu1733160@business.example.com",
            "amount":total_(request),
            "item_name":cart_id_(request),
            "invoice":str(uuid.uuid4()),
            "notify_url":request.build_absoluite_uri(reverse('paypal-pin')),
            "return":request.build_absolute_uri(reverse('return_view')),
            "cancel_return":request.build_absolute_uri(reverse('cancel_view')),
            "custom":"premium_plan",
            
        }
        #create the instance.
        form = PayPalPaymentsForm(initial=paypal_dict)
        context ={"form": form}
        return render(request, "checkout.html",context)

def return_view(request):
        return HttpResponse('Transaction Successful')

def cancel_view(request):
        return HttpResponse('Transaction Cancelled !')