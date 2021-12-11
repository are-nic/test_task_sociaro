from django.urls import path, include
from rest_framework_nested import routers
from rest_framework.routers import SimpleRouter

from .views import get_and_suggest_track, PartyView, RecommendTracksView

router = SimpleRouter(trailing_slash=False)

router.register('parties', PartyView, basename='parties')
party_router = routers.NestedSimpleRouter(router, 'parties', lookup='party')
party_router.register('recommend', RecommendTracksView, basename='recommend')

urlpatterns = [
    path('search-track', get_and_suggest_track)
]
urlpatterns += router.urls
urlpatterns += party_router.urls
