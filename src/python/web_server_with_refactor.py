import os
import socket
import traceback
from datetime import datetime
from typing import Tuple

# Webサーバーを表すクラス


class WebServer:
    # BASE_DIRとSTATIC_ROOTは、クラス変数。すべてのインスタンスが、このクラス変数を共有している
    # インスタンス変数は各インスタンスが持つ変数
    # 実行ファイルのあるディレクトリ
    # /Users/yuuki_haga/repos/server/web_server/src/python
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # 静的配信するファイルを置くディレクトリ
    # /Users/yuuki_haga/repos/server/web_server/src/python/static
    STATIC_ROOT = os.path.join(BASE_DIR, "static")

    # 拡張子とMIME Typeの対応
    # 最低限のMIME Typeを用意
    MIME_TYPES = {
        "html": "text/html",
        "css": "text/css",
        "png": "image/png",
        "jpg": "image/jpg",
        "gif": "image/gif",
    }

    def serve(self):
        print("===サーバーを起動します===")

        try:
            server_socket = self.create_server_socket()
            # 「クライアントからのコネクションを待つ」〜「コネクションを終了する」までの処理（31行目-97行目）をまるごと無限ループの中にいれた
            # リクエストの処理が完了すると、またループの先頭に戻り、次のリクエストを待ちます。
            # つまり、プログラムを起動した人が明示的にプログラムを中断させるまで、無限にリクエストをさばき続けるプログラムになります。
            while True:
                print("===クライアントからの接続を待ちます===")
                (client_socket, address) = server_socket.accept()
                print(f"===クライアントとの接続が完了しました remote_address: {address} ===")

                try:
                    # クライアントと通信をして、リクエストを処理をする
                    self.handle_client(client_socket)
                except Exception:
                    # リクエストの処理中に例外が発生した場合はコンソールにエラーログを出力し、
                    # 処理を続行する
                    print("===リクエストの処理中にエラーが発生しました===")
                    traceback.print_exec()
                finally:
                    # 例外が発生した場合も、発生しなかった場合も、TCP通信のcloseは行う
                    # try句の末尾でやってしまうと、途中で例外が発生した場合にコネクションの切断がスキップされてしまう
                    client_socket.close()
        finally:
            print("===サーバーを停止します。===")

    def create_server_socket(self) -> socket:
        server_socket = socket.socket()
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # socketをlocalhostのポート8080番に割り当てる
        server_socket.bind(("localhost", 8080))
        server_socket.listen(10)
        return server_socket

    # クライアントと接続済みのsocketを引数として受け取り、
    # リクエストを処理してレスポンスを送信する
    def handle_client(self, client_socket: socket) -> None:
        # クライアントから送られてきたデータを取得する
        request = client_socket.recv(4096)

        # クライアントから送られてきたデータをファイルに書き出す
        with open("server_recv.txt", "wb") as f:
            f.write(request)

        # HTTPリクエストをパースする
        method, path, http_version, request_header, request_body = self.parse_http_request(
            request)

        try:
            # ファイルからレスポンスボディを生成
            response_body = self.get_static_file_content(path)

            # レスポンスラインを生成
            response_line = "HTTP/1.1 200 OK\r\n"

        except OSError:
            # ファイルが見つからなかった場合は404を返す
            # ファイルが見つからなかった場合は404を返す
            not_found_file_path = os.path.join(
                self.STATIC_ROOT, "404.html")

            with open(not_found_file_path, "rb") as f:
                response_body = f.read()

            # レスポンスラインを生成
            response_line = "HTTP/1.1 404 Not Found\r\n"

        # レスポンスヘッダーを生成
        response_header = self.build_response_header(path, response_body)

        # レスポンス全体を生成する
        response = (response_line + response_header +
                    "\r\n").encode() + response_body

        # クライアントへレスポンスを送信する
        client_socket.send(response)

    def parse_http_request(self, request: bytes) -> Tuple[str, str, str, bytes, bytes]:
        """
        HTTPリクエストを
        1. method: str
        2. path: str
        3. http_version: str
        4. request_header: bytes
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

        return method, path, http_version, request_header, request_body

    def get_static_file_content(self, path: str) -> bytes:
        """
        リクエストpathから、staticファイルの内容を取得する
        """

        # pathの先頭の/を削除し、相対パスにしておく
        relative_path = path.lstrip("/")
        # ファイルのpathを取得
        static_file_path = os.path.join(self.STATIC_ROOT, relative_path)

        with open(static_file_path, "rb") as f:
            return f.read()

    # レスポンスヘッダーを構築する
    def build_response_header(self, path: str, response_body: bytes) -> str:
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


if __name__ == "__main__":
    server = WebServer()
    server.serve()
