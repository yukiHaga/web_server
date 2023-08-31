import re
import os
import textwrap
import urllib.parse
from pprint import pformat
import traceback
from datetime import datetime
from socket import socket
from threading import Thread
from typing import Tuple, Optional


# Threadはpythonの組み込みライブラリであるthreadingモジュールに含まれるクラスで、スレッドを簡単に作成するためのベースクラスである。
# Threadを利用する際は、Threadを継承したクラスを作成し、.run()メソッドをオーバーライドします。
# このクラスのインスタンスは.start()メソッドを呼び出すことで新しいスレッドを作成し、.run()メソッドにかかれた処理を開始します。
class WorkerThread(Thread):
    # 実行ファイルのあるディレクトリ
    # /Users/yuuki_haga/repos/server/web_server/src/python
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # 静的配信するファイルを置くディレクトリ
    # /Users/yuuki_haga/repos/server/web_server/src/python/static
    STATIC_ROOT = os.path.join(BASE_DIR, "static")

    # 拡張子とMIME Typeの対応
    # 最低限のMIME Typeを用意
    MIME_TYPES = {
        "html": "text/html; charset=UTF-8",
        "css": "text/css",
        "png": "image/png",
        "jpg": "image/jpg",
        "gif": "image/gif",
    }

    def __init__(self, client_socket: socket, address: Tuple[str, int]):
        # 親クラスの__init__メソッドを引数なしで呼び出す。
        super().__init__()

        self.client_socket = client_socket
        self.client_address = address

    # クライアントと接続済みのsocketを引数として受け取り、
    # リクエストを処理してレスポンスを送信する
    # runメソッドをオーバーライドする
    def run(self) -> None:
        try:
            request = self.client_socket.recv(4096)
            # クライアントから送られてきたデータをファイルに書き出す
            with open("server_recv.txt", "wb") as f:
                f.write(request)

            # HTTPリクエストをパースする
            method, path, http_version, request_header, request_body = self.parse_http_request(
                request)

            response_body: bytes
            # Optional[str]は、str型またはNoneを表す型
            content_type: Optional[str]
            response_line: str

            if path == "/now":
                html = f"""\
                    <html>
                    <body>
                      <h1>Now: {datetime.now()}</h1>
                    </body>
                    <html>
                """
                response_body = textwrap.dedent(html).encode()
                # 動的コンテンツを利用する場合、通常はpathからはレスポンスボディのフォーマットを特定することができないため、
                # Content-Typeを明示的に指定するようにしています。
                content_type = "text/html; charset=UTF-8"
                response_line = "HTTP/1.1 200 OK\r\n"
            # pathがそれ以外の時は、静的ファイルからレスポンスを生成する
            elif path == "/show_request":
                # pprint.pformat()は、辞書を改行を交えて見やすい文字列に変換してくれます。
                # .decode("utf-8","ignore")は、バイトデータをutf-8でデコードし、デコードできない文字は無視してそのまま表示します。
                # preタグで囲われた文字は入力されたソースのままHTMLに表示されることになります。
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

            elif path == "/parameters":
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
            else:
                try:
                    # ファイルからレスポンスボディを生成
                    response_body = self.get_static_file_content(path)

                    # 逆に、pathからContent-Typeを特定したい場合にはNoneを指定してあげるような実装にした。
                    content_type = None

                    # レスポンスラインを生成
                    response_line = "HTTP/1.1 200 OK\r\n"

                except OSError:
                    traceback.print_exec()
                    # ファイルが見つからなかった場合は404を返す
                    response_body = b"<html><body><h1>404 Not Found</h1></body></html>"
                    content_type = "text/html"
                    response_line = "HTTP/1.1 404 Not Found\r\n"

            # レスポンスヘッダーを生成
            response_header = self.build_response_header(
                path, response_body, content_type)

            # レスポンス全体を生成する
            response = (response_line + response_header +
                        "\r\n").encode() + response_body

            # クライアントへレスポンスを送信する
            self.client_socket.send(response)

        except Exception:
            # リクエストの処理中に例外が発生した場合はコンソールにエラーログを出力し、
            # 処理を続行する
            print("=== Worker: リクエストの処理中にエラーが発生しました ===")
            traceback.print_exc()

        finally:
            # 例外が発生した場合も、発生しなかった場合も、TCP通信のcloseは行う
            print(
                f"=== Worker: クライアントとの通信を終了します remote_address: {self.client_address} ===")
            self.client_socket.close()

    # ヘッダーはUTF-8でエンコードされた文字列だと決まっているのですが、
    # ボディは画像やPDFなど、文字列ではなくバイナリデータが送られてくる可能性があるため、常に文字列に変換できるとは限らないのです。
    def parse_http_request(self, request: bytes) -> Tuple[str, str, str, dict, bytes]:
        """
        HTTPリクエストを
        1. method: str
        2. path: str
        3. http_version: str
        4. request_header: dict
        5. request_body: bytes
        に分割/変換する
        """

        # リクエスト全体を
        # - リクエストライン(1行目)
        # - リクエストヘッダー(2行目〜空行)
        # - リクエストボディ(空行〜)
        # にパースする
        request_line, remain = request.split(b"\r\n", maxsplit=1)
        request_header, request_body = remain.split(b"\r\n\r\n", maxsplit=1)

        # リクエストラインを文字列に変換してパースする
        method, path, http_version = request_line.decode().split(" ")

        # リクエストヘッダーを辞書にパースする
        headers = {}
        for header_row in request_header.decode().split("\r\n"):
            # もしそのままバックスラッシュ等を表示させたい場合はクォーテーション前にrをつける。
            # raw文字列になる。
            # 正規表現の* は、* の直前の文字がないか、直前の文字が１個以上連続するという意味になる
            key, value = re.split(r": *", header_row, maxsplit=1)
            headers[key] = value

        return method, path, http_version, headers, request_body

    # リクエストpathから、staticファイルの内容を取得する
    def get_static_file_content(self, path: str) -> bytes:
        # pathの先頭の/を削除し、相対パスにしておく
        relative_path = path.lstrip("/")
        # ファイルのpathを取得
        static_file_path = os.path.join(self.STATIC_ROOT, relative_path)

        with open(static_file_path, "rb") as f:
            return f.read()

    # レスポンスヘッダーを構築する
    def build_response_header(self, path: str, response_body: bytes, content_type: Optional[str]) -> str:
        if content_type is None:
            # ヘッダー生成のためにContent-Typeを取得しておく
            # pathから拡張子を取得
            if "." in path:
                ext = path.rsplit(".", maxsplit=1)[-1]
            else:
                ext = ""
            # 拡張子からMIME Typeを取得
            # 知らない対応していない拡張子の場合はoctet-streamとする
            content_type = self.MIME_TYPES.get(ext, "application/octet-stream")

        response_header = ""
        response_header += f"Date: {datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}\r\n"
        response_header += "Host: HenaServer/0.1\r\n"
        response_header += f"Content-Length: {len(response_body)}\r\n"
        response_header += "Connection: Close\r\n"
        response_header += f"Content-Type: {content_type}\r\n"

        return response_header
