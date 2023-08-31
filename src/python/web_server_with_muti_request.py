import os
import socket
import traceback
from datetime import datetime

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
            server_socket = socket.socket()
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # socketをlocalhostのポート8080番に割り当てる
            server_socket.bind(("localhost", 8080))
            server_socket.listen(10)

            # 「クライアントからのコネクションを待つ」〜「コネクションを終了する」までの処理（31行目-97行目）をまるごと無限ループの中にいれた
            # リクエストの処理が完了すると、またループの先頭に戻り、次のリクエストを待ちます。
            # つまり、プログラムを起動した人が明示的にプログラムを中断させるまで、無限にリクエストをさばき続けるプログラムになります。
            while True:
                print("===クライアントからの接続を待ちます===")
                (client_socket, address) = server_socket.accept()
                print(f"===クライアントとの接続が完了しました remote_address: {address} ===")

                try:
                    # クライアントから送られてきたデータを取得する
                    request = client_socket.recv(4096)

                    # クライアントから送られてきたデータをファイルに書き出す
                    with open("server_recv.txt", "wb") as f:
                        f.write(request)

                    # リクエスト全体を
                    # 1. リクエストライン(1行目)
                    # 2. リクエストヘッダー(2行目 ~ 空行)
                    # 3. リクエストボディ(空行 ~)
                    # にパースする
                    request_line, remain = request.split(b"\r\n", maxsplit=1)
                    request_header, request_body = remain.split(
                        b"\r\n\r\n", maxsplit=1)

                    # 画像やcssを含んだhtmlをリクエストした場合、画像やcssを取得しにくる
                    # ===サーバーを起動します===
                    # ===クライアントからの接続を待ちます===
                    # ===クライアントとの接続が完了しました remote_address: ('127.0.0.1', 49213) ===
                    # GET /index.html HTTP/1.1
                    # ===クライアントからの接続を待ちます===
                    # ===クライアントとの接続が完了しました remote_address: ('127.0.0.1', 49215) ===
                    # GET /index.css HTTP/1.1
                    # ===クライアントからの接続を待ちます===
                    # ===クライアントとの接続が完了しました remote_address: ('127.0.0.1', 49217) ===
                    # GET /logo.png HTTP/1.1
                    # ===クライアントからの接続を待ちます===
                    # ===クライアントとの接続が完了しました remote_address: ('127.0.0.1', 49223) ===
                    # GET /favicon.ico HTTP/1.1
                    # ===クライアントからの接続を待ちます===
                    print(request_line.decode())

                    # リクエストラインをパースする
                    # request_line.decode()の戻り値は、GET / HTTP/1.1
                    # http://localhost:8080/index.htmlでアクセスすると、リクエストラインは、GET /index.html HTTP/1.1
                    method, path, http_version = request_line.decode().split(" ")

                    # Pythonのstr.lstripは、文字列の左端の文字を削除する
                    # pathの先頭の/を削除し、相対パスにしておく
                    # パスが絶対パスだと、relative_pathが空文字になる
                    relative_path = path.lstrip("/")

                    # ファイルのpathを取得
                    static_file_path = os.path.join(
                        self.STATIC_ROOT, relative_path)

                    # 例外処理をしておかないとループの途中で例外が発生した場合にプログラム全体が停止してしまいますが、
                    # 上記のようにハンドリングすることでその時扱っているリクエストの処理だけ中断させますが、プログラム全体は停止せずに次のループへ進むことになります。
                    try:
                        # ファイルからレスポンスボディを生成
                        with open(static_file_path, "rb") as f:
                            response_body = f.read()

                        # レスポンスラインを生成
                        response_line = "HTTP/1.1 200 OK\r\n"
                    except OSError:
                        # ファイルが見つからなかった場合は404を返す
                        not_found_file_path = os.path.join(
                            self.STATIC_ROOT, "404.html")

                        with open(not_found_file_path, "rb") as f:
                            response_body = f.read()

                        # レスポンスラインを生成
                        response_line = "HTTP/1.1 404 Not Found\r\n"

                    # ヘッダー生成のため、Content-Typeを取得しておく
                    # pathから拡張子を取得
                    if "." in path:
                        # rsplitは後ろから区切る。
                        # pathを.で分割し、リストで取得
                        # maxsplitは、分割する回数
                        # -1はリストの最後のインデックス
                        ext = path.rsplit(".", maxsplit=1)[-1]
                    else:
                        ext = ""

                    # 拡張子からMIME Typeを取得
                    # 知らない対応していない拡張子の場合はoctet-streamとする
                    # octet-streamは、ファイル形式が不明な場合に使うMIMEタイプ。
                    content_type = self.MIME_TYPES.get(
                        ext, "application/octet-stream")

                    # レスポンスヘッダーを生成
                    # ヘッダーの数が増えてソースコードの見通しが悪くなったり、コピペするのが疲れるぐらい改行コードが出てくるようになってから初めてリファクタリングすれば良いのです。
                    # そもそも勉強用だから、自分が理解できればOK
                    response_header = ""
                    # Dateでレスポンス生成日時を返すようにする
                    response_header += f"Date: {datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}\r\n"
                    # Serverヘッダーはレスポンスを生成したプログラムに関する情報を返す。
                    response_header += "Server: HenaHenaServer/0.1\r\n"
                    # Content-Lengthヘッダーは、レスポンスボディのバイト数を10進数で示す値を返す
                    # このヘッダーはマスト
                    response_header += f"Content-Length: {len(response_body)}\r\n"
                    # HTTP/1.1では通信はデフォルトでコネクションの再利用をすることになっており、 コネクションの再利用に対応していないサーバーはConnection: Closeを返却しなければならない
                    # そのため、返している。
                    response_header += "Connection: Close\r\n"
                    # このヘッダーは省略してしまうと「正体不明のファイル」として扱われてしまいブラウザの画面で表示されないことがありますので、きちんと内容にあったものを返す。
                    response_header += f"Content-Type: {content_type}\r\n"

                    # ヘッダーとボディを空行でくっつけた上でbytesに変換して、レスポンス全体を生成する
                    response = (response_line + response_header +
                                "\r\n").encode() + response_body

                    # クライアントへレスポンスを送信する
                    client_socket.send(response)
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


if __name__ == "__main__":
    server = WebServer()
    server.serve()
