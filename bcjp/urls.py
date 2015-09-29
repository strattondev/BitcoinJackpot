from django.conf.urls import include, patterns, url, handler400, handler403, handler404, handler500
from bcjp import views, admin
from bcjp.bcjp_utils import start_up_new_round

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^(?P<secret_id>(\d+)(-).+)$', views.index_with_secret, name="index_with_secret"),
    url(r'^about$', views.about, name="about"),
    url(r'^provably$', views.provably, name="provably"),
    url(r'^toc$', views.terms_and_conditions, name="terms_and_conditions"),
    url(r'^stats$', views.stats, name="stats"),
    url(r'^hide_how_it_works$', views.hide_how_it_works, name="hide_how_it_works"),
    url(r'^first/time$', views.first_time, name="first_time"),
    url(r'^betting/log$', views.betting_log, name="betting_log"),
    url(r'^betting/track/(?P<secret>.+)/(?P<first48>.+)$', views.betting_track, name="betting_track"),
    url(r'^betting/withdraw$', views.betting_withdraw, name="betting_withdraw"),
    url(r'^betting/withdraw/address$', views.betting_withdraw_address, name="betting_withdraw_address"),
    url(r'^betting/place$', views.betting_place, name="betting_place"),
    url(r'^round/log$', views.round_log, name="round_log"),
    url(r'^round/progress$', views.round_progress, name="round_progress"),
    url(r'^admin/bet$', admin.create_bet, name="admin_create_bet"),
    url(r'^admin/topup$', admin.top_up, name="admin_top_up"),
]

start_up_new_round()