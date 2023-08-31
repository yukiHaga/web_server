import os
import traceback
import settings
from henango.http.request import HTTPRequest
from henango.http.response import HTTPResponse


def static(request: HTTPRequest) -> HTTPResponse:
    """
    静的ファイルからレスポンスを取得する
    """

    try:
        static_root = getattr(settings, "STATIC_ROOT")

        # pathの先頭の/を削除し、相対パスにしておく
        relative_path = request.path.lstrip("/")
        # ファイルのpathを取得
        static_file_path = os.path.join(static_root, relative_path)

        # withはクロージング処理を自動化しているだけだから、別スコープとかではない
        with open(static_file_path, "rb") as f:
            response_body = f.read()

        # 逆に、pathからContent-Typeを特定したい場合にはNoneを指定してあげるような実装にした。
        content_type = None
        return HTTPResponse(status_code=200, content_type=content_type, body=response_body)
    except OSError:
        traceback.print_exec()
        # ファイルが見つからなかった場合は404を返す
        response_body = b"<html><body><h1>404 Not Found</h1></body></html>"
        content_type = "text/html"
        return HTTPResponse(status_code=404, content_type=content_type, body=response_body)
