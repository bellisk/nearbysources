from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^/?$', 'nearbysources.questions.views.frontpage'),
    url(r'^q/([0-9]+)/([0-9]+)/([a-z-]+)/$', 'nearbysources.questions.views.questionnaire'),
    url(r'^q/([0-9]+)/([0-9]+)/([a-z-]+)/submit_response$', 'nearbysources.questions.views.submit_response'),
    url(r'^q/([0-9]+)/([0-9]+)/([a-z-]+)/thankyou$', 'nearbysources.questions.views.thankyou'),
)
