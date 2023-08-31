import views_with_http as views
from henango.urls.pattern import URLPattern

# pathとview関数の対応
# URL_VIEW = {
#     "/now": views.now,
#     "/show_request": views.show_request,
#     "/parameters": views.parameters,
#     "/user/<user_id>/profile": views.user_profile,
# }
# これでも他のエンジニアからしたら、「なんでURLPatternで囲まないといけないの？」ってなりそう。若干ハイコンテキスト。
url_patterns = [
    URLPattern("/now", views.now),
    URLPattern("/show_request", views.show_request),
    URLPattern("/parameters", views.parameters),
    URLPattern("/user/<user_id>/profile", views.user_profile),
]
