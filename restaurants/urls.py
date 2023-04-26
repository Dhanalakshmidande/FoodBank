from django.urls import path
from .views import RestaurantListView, RestaurantDetailView,\
    RestaurantCreateView, RestaurantUpdateView, RestaurantDeleteView,\
    MyPostView,checkout,return_view,cancel_view,cart_view

urlpatterns = [
    path('', RestaurantListView.as_view(), name='home'),
    path('create/', RestaurantCreateView.as_view(), name='create'),
    path('<slug:slug>/', RestaurantDetailView.as_view(), name='detail'),
    path('<slug:slug>/update', RestaurantUpdateView.as_view(), name='update'),
    path('<slug:slug>/delete', RestaurantDeleteView.as_view(), name='delete'),
    path('dashboard/myposts/', MyPostView.as_view(), name='my_posts'),
    path('<int:product_id>/<slug:slug>/', RestaurantDetailView.as_view(), name='detail'),
    path('cart/',cart_view, name = 'cart_view'),
    path('checkout/',checkout, name = 'checkout'),
    path('success/',return_view, name = 'return_view'),
    path('cancel/',cancel_view, name = 'cancel_view'),
]
