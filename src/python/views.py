# views.pyは、pathごとに応じた関数を持ち、リクエストの内容を受け取り動的に生成したレスポンスの内容を返す
import textwrap
import urllib.parse
from datetime import datetime
from pprint import pformat
from typing import Tuple, Optional

# 現在時刻を表示するHTMLを生成する


def now(
    method: str,
    path: str,
    http_version: str,
    request_header: dict,
    request_body: bytes
) -> Tuple[bytes, Optional[str], str]:
    html = f"""\
        <html>
        <body>
            <h1>Now: {datetime.now()}</h1>
        </body>
        <html>
    """
    response_body = textwrap.dedent(html).encode()
    content_type = "text/html; charset=UTF-8"
    response_line = "HTTP/1.1 200 OK\r\n"

    return response_body, content_type, response_line

# HTTPリクエストの内容を表示するHTMLを生成する


def show_request(
    method: str,
    path: str,
    http_version: str,
    request_header: dict,
    request_body: bytes
) -> Tuple[bytes, Optional[str], str]:
    html = f"""\
        <html>
        <body>
            <h1>Request Line:</h1>
            <p>
                {method} {path} {http_version}
            </p>
            <h1>Headers:</h1>
            <pre>{pformat(request_header)}</pre>
            <h1>Body:</h1>
            <pre>{request_body.decode("utf-8", "ignore")}</pre>
        </body>
        </html>
    """
    response_body = textwrap.dedent(html).encode()

    content_type = "text/html; charset=UTF-8"

    response_line = "HTTP/1.1 200 OK\r\n"

    return response_body, content_type, response_line

# 関数内ではこれらの引数は使わないのですが、受け取れるようにしておいてあげることで、
# 呼び出す側は「何が必要で何が不要」かは考えなくて済むようになります。


def parameters(
    method: str,
    path: str,
    http_version: str,
    request_header: dict,
    request_body: bytes
) -> Tuple[bytes, Optional[str], str]:
    if method == "GET":
        response_body = b"<html><body><h1>405 Method Not Allowed</h1></body></html>"
        content_type = "text/html; charset=UTF-8"
        # 405 Method Not Allowedは、URLがリクエストのメソッドに対応していない（または許可していない）ことをクライアントへ伝えるためのステータスです。
        response_line = "HTTP/1.1 405 Method Not Allowed\r\n"
    elif method == "POST":
        # urllib.parse.parse_qs()は、URLエンコードされた文字列を辞書へパースする関数です。
        # 辞書のキーは項目名でstr型ですが、同じ項目名で複数のデータが送られてくるのに対応するため辞書の値は常に（1個しかなくても）list型になっていることに注意してください。
        post_params = urllib.parse.parse_qs(request_body.decode())
        html = f"""\
            <html>
            <body>
                <h1>Parameters:</h1>
                <pre>{pformat(post_params)}</pre>
            </body>
            </html>
        """
        response_body = textwrap.dedent(html).encode()

        content_type = "text/html; charset=UTF-8"

        response_line = "HTTP/1.1 200 OK\r\n"

    return response_body, content_type, response_line
