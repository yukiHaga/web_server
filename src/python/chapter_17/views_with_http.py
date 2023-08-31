# views.pyは、pathごとに応じた関数を持ち、リクエストの内容を受け取り動的に生成したレスポンスの内容を返す
# コネクションがどうとか、ヘッダーのパースがこうとか、そういったHTTPの事情は関知せず、見た目(view)の部分（= リクエストボディ）を生成することだけを責務として持つモジュール
import textwrap
import urllib.parse
from datetime import datetime
from pprint import pformat
from typing import Tuple, Optional

from henango.http.request import HTTPRequest
from henango.http.response import HTTPResponse


# 現在時刻を表示するHTMLを生成する


# viewクラスはあくまで「動的なレスポンスの内容を生成する」ことだけに専念させ、HTTPのルールや慣習は極力扱わせないようにするためです。
def now(request: HTTPRequest) -> HTTPResponse:
    html = f"""\
        <html>
        <body>
            <h1>Now: {datetime.now()}</h1>
        </body>
        <html>
    """
    body = textwrap.dedent(html).encode()
    content_type = "text/html; charset=UTF-8"

    return HTTPResponse(status_code=200, content_type=content_type, body=body)

# HTTPリクエストの内容を表示するHTMLを生成する


def show_request(request: HTTPRequest) -> HTTPResponse:
    html = f"""\
        <html>
        <body>
            <h1>Request Line:</h1>
            <p>
                {request.method} {request.path} {request.http_version}
            </p>
            <h1>Headers:</h1>
            <pre>{pformat(request.headers)}</pre>
            <h1>Body:</h1>
            <pre>{request.body.decode("utf-8", "ignore")}</pre>
        </body>
        </html>
    """
    body = textwrap.dedent(html).encode()
    content_type = "text/html; charset=UTF-8"

    return HTTPResponse(status_code=200, content_type=content_type, body=body)

# 関数内ではこれらの引数は使わないのですが、受け取れるようにしておいてあげることで、
# 呼び出す側は「何が必要で何が不要」かは考えなくて済むようになります。


def parameters(request: HTTPRequest) -> HTTPResponse:
    if request.method == "GET":
        body = b"<html><body><h1>405 Method Not Allowed</h1></body></html>"
        content_type = "text/html; charset=UTF-8"
        # 405 Method Not Allowedは、URLがリクエストのメソッドに対応していない（または許可していない）ことをクライアントへ伝えるためのステータスです。
        status_code = 405
    elif request.method == "POST":
        # urllib.parse.parse_qs()は、URLエンコードされた文字列を辞書へパースする関数です。
        # 辞書のキーは項目名でstr型ですが、同じ項目名で複数のデータが送られてくるのに対応するため辞書の値は常に（1個しかなくても）list型になっていることに注意してください。
        post_params = urllib.parse.parse_qs(request.body.decode())
        html = f"""\
            <html>
            <body>
                <h1>Parameters:</h1>
                <pre>{pformat(post_params)}</pre>
            </body>
            </html>
        """
        body = textwrap.dedent(html).encode()
        content_type = "text/html; charset=UTF-8"
        status_code = 200

    return HTTPResponse(status_code=status_code, content_type=content_type, body=body)
