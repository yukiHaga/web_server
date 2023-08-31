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

import views
from henango.http.request import HTTPRequest
from henango.http.response import HTTPResponse


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

    URL_VIEW = {
        "/now": views.now,
        "/show_request": views.show_request,
        "/parameters": views.parameters,
    }

    # ステータスコードとステータスラインの対応
    STATUS_LINES = {
        200: "200 OK",
        404: "404 Not Found",
        405: "405 Method Not Allowed",
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
            request_bytes = self.client_socket.recv(4096)
            # クライアントから送られてきたデータをファイルに書き出す
            with open("server_recv.txt", "wb") as f:
                f.write(request_bytes)

            # HTTPリクエストをパースする
            request = self.parse_http_request(request_bytes)

            # 注目すべきなのは、全てのview関数が同じ引数(method, path, http_version, request_header, request_body)を受け取るようになったことで、
            # view関数が抽象化されている点です。
            # 以前までは関数ごとに引数が違ったので、ひとくちに「view関数を呼び出す」と言っても「その関数が具体的になんという関数なのか」が
            # 分からないと正しく呼び出せませんでした。
            # しかし、引数が統一（= インターフェースが統一）されることで、 「具体的に何ていう関数なのかは知らないけど、とにかく呼び出せる」
            # ようになっているのです。
            if request.path in self.URL_VIEW:
                response = self.URL_VIEW[request.path](request)
            # pathがそれ以外の時は、静的ファイルからレスポンスを生成する
            else:
                try:
                    # ファイルからレスポンスボディを生成
                    response_body = self.get_static_file_content(request.path)

                    # 逆に、pathからContent-Typeを特定したい場合にはNoneを指定してあげるような実装にした。
                    content_type = None

                    response = HTTPResponse(
                        status_code=200, content_type=content_type, body=response_body)

                except OSError:
                    traceback.print_exec()
                    # ファイルが見つからなかった場合は404を返す
                    response_body = b"<html><body><h1>404 Not Found</h1></body></html>"
                    content_type = "text/html"
                    response = HTTPResponse(
                        status_code=404, content_type=content_type, body=response_body)

            # レスポンスラインを生成
            response_line = self.build_response_line(response)

            # レスポンスヘッダーを生成
            response_header = self.build_response_header(response, request)

            # レスポンス全体を生成する
            response_bytes = (response_line + response_header +
                              "\r\n").encode() + response.body

            # クライアントへレスポンスを送信する
            self.client_socket.send(response_bytes)

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
    def parse_http_request(self, request_bytes: bytes) -> HTTPRequest:
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
        request_line, remain = request_bytes.split(b"\r\n", maxsplit=1)
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

        return HTTPRequest(method=method, path=path, http_version=http_version, headers=headers, body=request_body)

    # リクエストpathから、staticファイルの内容を取得する
    def get_static_file_content(self, path: str) -> bytes:
        # pathの先頭の/を削除し、相対パスにしておく
        relative_path = path.lstrip("/")
        # ファイルのpathを取得
        static_file_path = os.path.join(self.STATIC_ROOT, relative_path)

        with open(static_file_path, "rb") as f:
            return f.read()

    # レスポンスラインを構築する
    def build_response_line(self, response: HTTPResponse) -> str:
        status_line = self.STATUS_LINES[response.status_code]
        return f"HTTP/1.1 {status_line}"

    # レスポンスヘッダーを構築する
    def build_response_header(self, response: HTTPResponse, request: HTTPRequest) -> str:
        if response.content_type is None:
            # ヘッダー生成のためにContent-Typeを取得しておく
            # pathから拡張子を取得
            if "." in request.path:
                ext = request.path.rsplit(".", maxsplit=1)[-1]
            else:
                ext = ""
            # 拡張子からMIME Typeを取得
            # 知らない対応していない拡張子の場合はoctet-streamとする
            content_type = self.MIME_TYPES.get(ext, "application/octet-stream")

        response_header = ""
        response_header += f"Date: {datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}\r\n"
        response_header += "Host: HenaServer/0.1\r\n"
        response_header += f"Content-Length: {len(response.body)}\r\n"
        response_header += "Connection: Close\r\n"
        response_header += f"Content-Type: {response.content_type}\r\n"

        return response_header
