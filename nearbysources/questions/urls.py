from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^/?$', 'nearbysources.questions.views.frontpage'),
    url(r'^q/([0-9]+)/([0-9]+)/([a-z-]+)/$', 'nearbysources.questions.views.questionnaire'),
    url(r'^q/([0-9]+)/([0-9]+)/([a-z-]+)/submit_response$', 'nearbysources.questions.views.submit_response'),
    url(r'^q/([0-9]+)/([0-9]+)/([a-z-]+)/thankyou$', 'nearbysources.questions.views.thankyou'),
    url(r'^q/([0-9]+)/([a-z-]+)/$', 'nearbysources.questions.views.info'),
    url(r'^q/([0-9]+)/([a-z-]+)/search$', 'nearbysources.questions.views.search'),
    url(r'^q/([0-9]+)/([a-z-]+)/results$', 'nearbysources.questions.views.results'),
    url(r'^q/([0-9]+)/([a-z-]+)/csvresults.csv$', 'nearbysources.questions.views.csvresults'),
    url(r'^q/([0-9]+)/([a-z-]+)/jsonresults.json$', 'nearbysources.questions.views.jsonresults'),
    url(r'^q/([0-9]+)/([a-z-]+)/kmlresults.kml$', 'nearbysources.questions.views.kmlresults'),
    url(r'^q/([0-9]+)/([a-z-]+)/get_all_questions_and_locations$', 'nearbysources.questions.views.get_all_questions_and_locations'),
)
