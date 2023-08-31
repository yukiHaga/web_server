# これがviewのロジックってことか
# djangoのviewはRailsのコントローラのような振る舞いをしている
# views.pyは、pathごとに応じた関数を持ち、リクエストの内容を受け取り動的に生成したレスポンスの内容を返す
# コネクションがどうとか、ヘッダーのパースがこうとか、そういったHTTPの事情は関知せず、見た目(view)の部分（= リクエストボディ）を生成することだけを責務として持つモジュール
import textwrap
import urllib.parse
from datetime import datetime
from pprint import pformat
from typing import Tuple, Optional

from henango.http.request import HTTPRequest
from henango.http.response import HTTPResponse
from henango.template.renderer import render
from henango.http.cookie import Cookie


# viewクラスはあくまで「動的なレスポンスの内容を生成する」ことだけに専念させ、HTTPのルールや慣習は極力扱わせないようにするためです。
def now(request: HTTPRequest) -> HTTPResponse:
    """
    現在時刻を表示するHTMLを生成する
    """
    # with open("./templates/now.html") as f:
    #     template = f.read()
    #     # format() メソッドは、指定された値をフォーマットして文字列のプレースホルダに挿入します。
    #     # プレースホルダは波括弧で定義します：{}.プレースホルダについての詳細は、以下のプレースホルダのセクションを参照ください。
    #     html = template.format(now=datetime.now())
    # html = render("./templates/now.html", {"now": datetime.now()})

    # エンコード処理を入れた場合
    # html = render("now.html", {"now": datetime.now()})
    # # body = textwrap.dedent(html).encode()
    # body = html.encode()

    # エンコード処理を入れない場合
    body = render("now.html", {"now": datetime.now()})
    return HTTPResponse(body=body)

# HTTPリクエストの内容を表示するHTMLを生成する


def show_request(request: HTTPRequest) -> HTTPResponse:
    context = {
        "request": request,
        "headers": pformat(request.headers),
        "body": request.body.decode("utf-8", "ignore")
    }
    body = render("show_request.html", context)
    return HTTPResponse(body=body)

# 関数内ではこれらの引数は使わないのですが、受け取れるようにしておいてあげることで、
# 呼び出す側は「何が必要で何が不要」かは考えなくて済むようになります。


def parameters(request: HTTPRequest) -> HTTPResponse:
    """
    POSTパラメータを表示するHTMLを表示する
    """
    if request.method == "GET":
        body = b"<html><body><h1>405 Method Not Allowed</h1></body></html>"
        # 405 Method Not Allowedは、URLがリクエストのメソッドに対応していない（または許可していない）ことをクライアントへ伝えるためのステータスです。
        status_code = 405
        return HTTPResponse(status_code=status_code, body=body)

    elif request.method == "POST":
        # urllib.parse.parse_qs()は、URLエンコードされた文字列を辞書へパースする関数です。
        # 辞書のキーは項目名でstr型ですが、同じ項目名で複数のデータが送られてくるのに対応するため辞書の値は常に（1個しかなくても）list型になっていることに注意してください。
        post_params = urllib.parse.parse_qs(request.body.decode())
        context = {"params": pformat(post_params)}
        body = render("parameters.html", context)
        return HTTPResponse(body=body)


def user_profile(request: HTTPRequest) -> HTTPResponse:
    context = {"user_id": request.params["user_id"]}
    body = render("user_profile.html", context)
    return HTTPResponse(body=body)

def set_cookie(request: HTTPRequest) -> HTTPResponse:
    return HTTPResponse(headers={"Set-Cookie": "username=YUKI"})

def login(request: HTTPRequest) -> HTTPResponse:
    if request.method == "GET":
        body = render("login.html", {})
        return HTTPResponse(body=body)
    elif request.method == "POST":
        post_params = urllib.parse.parse_qs(request.body.decode())
        username = post_params["username"][0]
        email = post_params["email"][0]

        # Cookieの有効期限(Max-Age属性)を30sに設定
        cookies = [
            Cookie(name="username", value=username, max_age=30),
            Cookie(name="email", value=email, max_age=30)
        ]

        # headers = {"Location": "/welcome", "Set-Cookie": f"username={username}"}
        # return HTTPResponse(status_code=302, headers=headers)
        return HTTPResponse(status_code=302, headers={"Location": "/welcome"}, cookies=cookies)

def welcome(request: HTTPRequest) -> HTTPResponse:
    # cookieを扱うたびにこの処理を書くのは辛い
    # cookie_header = request.headers.get("Cookie", None)

    # # Cookieが送信されていなければ、ログインしていないとみなして /loginへリダイレクト
    # if not cookie_header:
    #     return HTTPResponse(status_code=302, headers={"Location": "/login"})

    # # str から list へ変換
    # # ex) "name1=value1; name2=value2" => ["name1=value1", "name2=value2"]
    # cookie_strings = cookie_header.split("; ")

    # # list から dict へ変換
    # # ex) ["name1=value1", "name2=value2"] => {"name1": "value1", "name2": "value2"}
    # cookies = {}
    # for cookie_string in cookie_strings:
    #     name, value = cookie_string.split("=", maxsplit=1)
    #     cookies[name] = value

    # # Cookieにusernameが含まれていなければ、ログインしていないとみなして/loginへリダイレクト
    # if "username" not in cookies:
    #     return HTTPResponse(status_code=302, headers={"Location": "/login"})

    # # Welcome画面を表示
    # body = render("welcome.html", context={"username": cookies["username"]})

    # return HTTPResponse(body=body)

    ## dictのキーにusernameがあるかどうかをチェックしている
    if "username" not in request.cookies:
        return HTTPResponse(status_code=302, headers={"Location": "/login"})

    username = request.cookies["username"]
    email = request.cookies["email"]
    body = render("welcome.html", context={"username": username, "email": email})

    return HTTPResponse(body=body)

