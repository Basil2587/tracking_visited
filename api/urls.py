from django.urls import path
from . import views


urlpatterns = {
    path('visited_links', views.save_visited_links),
    path('visited_domains', views.get_visited),
    path('items', views.manage_items, name="items"),
}
