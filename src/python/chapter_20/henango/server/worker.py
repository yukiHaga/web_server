import re
import os
import textwrap
import urllib.parse
from pprint import pformat
import traceback
from datetime import datetime
from re import Match
from socket import socket
from threading import Thread
from typing import Tuple, Optional

import settings
from henango.http.request import HTTPRequest
from henango.http.response import HTTPResponse
from henango.urls.resolver import URLResolver


# Threadはpythonの組み込みライブラリであるthreadingモジュールに含まれるクラスで、スレッドを簡単に作成するためのベースクラスである。
# Threadを利用する際は、Threadを継承したクラスを作成し、.run()メソッドをオーバーライドします。
# このクラスのインスタンスは.start()メソッドを呼び出すことで新しいスレッドを作成し、.run()メソッドにかかれた処理を開始します。
class Worker(Thread):
    # 拡張子とMIME Typeの対応
    # 最低限のMIME Typeを用意
    MIME_TYPES = {
        "html": "text/html; charset=UTF-8",
        "css": "text/css",
        "png": "image/png",
        "jpg": "image/jpg",
        "gif": "image/gif",
    }

    # ステータスコードとステータスラインの対応
    # ステータスコード302は一時的なリダイレクトを意味し、ブラウザはLocationヘッダーで指定されたURLへ再度リクエストをし直してくれます。
    STATUS_LINES = {
        200: "200 OK",
        404: "404 Not Found",
        405: "405 Method Not Allowed",
        302: "302 Found",
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
            print(request.path)

            # pythonのfor-else文を使っている
            # for句が最後まで実行された（＝途中でbreakが呼ばれなかった）場合のみ、else句が実行されます。
            # 今までは単純にURL_VIEW辞書のキーとpathが文字列として一致するかどうかでviewを検索していましたが、
            # 今回からは判定ロジックが複雑になるためself.url_match()というメソッドを新しく作成してその中で判定するようにしました。
            # itemsは辞書のキーとバリューをセットとして返す
            # それをfor文で取り出している
            # for url_pattern, view in URL_VIEW.items():
            #     match = self.url_match(url_pattern, request.path)
            #     if match:
            #         # ここでrequestにparamsを追加している
            #         request.params.update(match.groupdict())
            #         response = view(request)
            #         break
            # 以下もリファクタリングで変更した(マッチング判定を外部モジュールに切り出せたのはいいですが、URL解決処理はまだまだworkerに残っているため)
            # for url_pattern in url_patterns:
            #     match = url_pattern.match(request.path)
            #     if match:
            #         request.params.update(match.groupdict())
            #         response = url_pattern.view(request)
            #         break

            # URL解決(pathから目当てのviewを取得する処理)を試みる
            # URL解決のための処理が外部に切り出せたおかげで、WorkerクラスはURL解決の方法について何も知らなくて良くなり、また一つ責務が減りました。
            view = URLResolver().resolve(request)

            # レスポンスを生成する
            response = view(request)

            # インターフェースを共通にして抽象化したから、if文の条件分岐が必要じゃなくなった。
            # # pathがそれ以外の時は、静的ファイルからレスポンスを生成する
            # else:
            #     try:
            #         # ファイルからレスポンスボディを生成
            #         response_body = self.get_static_file_content(request.path)

            #         # 逆に、pathからContent-Typeを特定したい場合にはNoneを指定してあげるような実装にした。
            #         content_type = None

            #         response = HTTPResponse(
            #             status_code=200, content_type=content_type, body=response_body)

            #     except OSError:
            #         traceback.print_exec()
            #         # ファイルが見つからなかった場合は404を返す
            #         response_body = b"<html><body><h1>404 Not Found</h1></body></html>"
            #         content_type = "text/html"
            #         response = HTTPResponse(
            #             status_code=404, content_type=content_type, body=response_body)

            # レスポンスボディを変換
            # isinstance 関数は 1 番目の引数に指定したオブジェクトが 2 番目の引数に指定したデータ型と等しいかどうかを返します。
            # 実際のHTTPレスポンスを生成する処理の直前に、bodyがstr型だったらbytes型へ変換する、という処理を追加しました。
            # これで、view関数側ではbodyはstr型のまま渡してしまって大丈夫になりました。
            # このやり方は強引だからあんま好きじゃない。あと、これを初めて見た人がなぜこんな処理わざわざ書いているの？ってなりそう。肩も満たしていないし。
            if isinstance(response.body, str):
                response.body = response.body.encode()

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

        cookies = {}
        if "Cookie" in headers:
            cookie_strings = headers["Cookie"].split("; ")
            for cookie_string in cookie_strings:
                name, value = cookie_string.split("=", maxsplit=1)
                cookies[name] = value

        return HTTPRequest(method=method, path=path, http_version=http_version, headers=headers, cookies=cookies, body=request_body)

    # リクエストpathから、staticファイルの内容を取得する
    # def get_static_file_content(self, path: str) -> bytes:
    #     default_static_root = os.path.join(
    #         os.path.dirname(__file__), "../../static")
    #     # settingsモジュールにSTATIC_ROOTという値があればそれを取得して、なければデフォルトの値を使用する
    #     static_root = getattr(settings, "STATIC_ROOT", default_static_root)

    #     # pathの先頭の/を削除し、相対パスにしておく
    #     relative_path = path.lstrip("/")
    #     # ファイルのpathを取得
    #     static_file_path = os.path.join(static_root, relative_path)

    #     with open(static_file_path, "rb") as f:
    #         return f.read()

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
                # 拡張子からMIME Typeを取得
                # 知らない対応していない拡張子の場合はoctet-streamとする
                response.content_type = self.MIME_TYPES.get(
                    ext, "application/octet-stream")
            else:
                # pathに拡張子がない場合はhtml扱いとする
                # 本当はHTTPResponseオブジェクトのcontent_type属性のデフォルト値として設定したいのですが、
                # 本教材では静的ファイル配信の実装方法がちょっと特殊なため、このようにしています。
                response.content_type = "text/html; charset=UTF-8"

        response_header = ""
        response_header += f"Date: {datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}\r\n"
        response_header += "Host: HenaServer/0.1\r\n"
        response_header += f"Content-Length: {len(response.body)}\r\n"
        response_header += "Connection: Close\r\n"
        response_header += f"Content-Type: {response.content_type}\r\n"

        for cookie_name, cookie_value in response.cookies.items():
            response_header += f"Set-Cookie: {cookie_name}={cookie_value}\r\n"

        # レスポンスが元々持っているヘッダーもresponse_headerに含める
        for header_name, header_value in response.headers.items():
            response_header += f"{header_name}: {header_value}\r\n"

        return response_header

    # def url_match(self, url_pattern: str, path: str) -> Optional[Match]:
    #     # 最初の引数 r"<(.+?)>" は、< と > で囲まれた任意の文字列をキャプチャする正規表現パターンです。
    #     # (.+?) は、最小限の文字列をマッチさせる非貪欲なキャプチャグループです。
    #     # 2番目の引数 r"(?P<\1>[^/]+)" は、<...> でキャプチャされた部分を捕捉するための正規表現パターンです。
    #     # ?P<\1> は、<...> 内の文字列をグループ化し、その名前を捕捉するための構文です。
    #     # [^/]+ は、スラッシュ以外の文字列を意味し、キャプチャする文字列を表しています。
    #     # re.sub() 関数は、指定した正規表現パターンにマッチする文字列を、2番目の引数で指定した文字列に置換します。
    #     # この場合、URLパターン内の <...> をキャプチャグループに変換しています。
    #     # URLパターンを正規表現パターンに変換する
    #     # ex) '/user/<user_id>/profile' => '/user/(?P<user_id>[^/]+)/profile'
    #     # re.subは第一引数が正規表現、第二引数が置換する文字列(正規表現でヒットした文字列がこの文字列に切り替わる)、第三引数が正規表現をかける対象の文字列
    #     # もし何もマッチしない場合、元のテキストが返される
    #     re_pattern = re.sub(r"<(.+?)>", r"(?P<\1>[^/]+)", url_pattern)
    #     # re_pattern /now
    #     # re_pattern /show_request
    #     # re_pattern /parameters
    #     # re_pattern /user/(?P<user_id>[^/]+)/profile
    #     # (?P<name>pattern)は名前付きグループといって、マッチしたグループを後から.groupdict()などを使って名前で取り出すことができます。
    #     print("re_pattern", re_pattern)
    #     return re.match(re_pattern, path)
