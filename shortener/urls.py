from django.urls import path
from . import views

app_name = "shortener"

urlpatterns = [
    path("", views.index_view, name="index"),
    path("info/<str:code>/", views.info_view, name="info"),
    path("qr/<str:code>/", views.qr_download_view, name="qr_download"),
    path("delete/<str:code>/", views.delete_link_view, name="delete"),
    path("api/links/", views.api_links_view, name="api_links"),
    path("api/links/<str:code>/", views.api_link_detail_view, name="api_link_detail"),
    path("<str:code>/", views.redirect_view, name="redirect"),
]
