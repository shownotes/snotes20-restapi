from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import patterns, include, url
from django.contrib import admin

from rest_framework import routers

import snotes20.views
import statistic.urls

router = routers.DefaultRouter()

router.register(r'auth', snotes20.views.AuthViewSet, base_name='auth')
router.register(r'users', snotes20.views.UserViewSet, base_name='users')
router.register(r'soonepisodes', snotes20.views.SoonEpisodeViewSet, base_name='sonnepisodes')
router.register(r'documents', snotes20.views.DocumentViewSet, base_name='documents')
router.register(r'importerlogs', snotes20.views.ImporterLogViewSet, base_name='importerlogs')
router.register(r'editors', snotes20.views.EditorViewSet, base_name='editors')
router.register(r'archive', snotes20.views.ArchiveViewSet, base_name='archive')
router.register(r'podcasts', snotes20.views.PodcastViewSet, base_name='podcasts')
router.register(r'pepisodes', snotes20.views.PrivateEpisodeViewSet, base_name='pepsidoes')

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^docs/', include('rest_framework_swagger.urls')),
    url(r'^statistic/', include(statistic.urls)),
    url(r'^', include(router.urls)),
)

if settings.DEBUG:
    urlpatterns += static('media', document_root=settings.MEDIA_ROOT)
