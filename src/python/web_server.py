import socket
from datetime import datetime

# Webサーバーを表すクラス


class WebServer:
    def serve(self):
        print("===サーバーを起動します===")

        try:
            server_socket = socket.socket()
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # socketをlocalhostのポート8080番に割り当てる
            server_socket.bind(("localhost", 8080))
            server_socket.listen(10)

            print("===クライアントからの接続を待ちます===")
            (client_socket, address) = server_socket.accept()
            print(f"===クライアントとの接続が完了しました remote_address: {address} ===")

            # クライアントから送られてたデータを取得する
            request = client_socket.recv(4096)

            # クライアントから送られてきたデータをファイルに書き出す
            with open("server_recv.txt", "wb") as f:
                f.write(request)

            # レスポンスボディを生成
            response_body = "<html><body><h1>It works! this is perfect server</h1></body></html>"

            # レスポンスラインを生成
            response_line = "HTTP/1.1 200 OK\r\n"

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
            response_header += f"Content-Length: {len(response_body.encode())}\r\n"
            # HTTP/1.1では通信はデフォルトでコネクションの再利用をすることになっており、 コネクションの再利用に対応していないサーバーはConnection: Closeを返却しなければならない
            # そのため、返している。
            response_header += "Connection: Close\r\n"
            # このヘッダーは省略してしまうと「正体不明のファイル」として扱われてしまいブラウザの画面で表示されないことがありますので、きちんと内容にあったものを返す。
            response_header += "Content-Type: text/html\r\n"

            # ヘッダーとボディを空行でくっつけた上でbytesに変換して、レスポンス全体を生成する
            response = (response_line + response_header +
                        "\r\n" + response_body).encode()

            # クライアントレスポンスを送信する
            client_socket.send(response)

            # 通信を終了させる
            client_socket.close()

        finally:
            print("===サーバーを停止します。===")


if __name__ == "__main__":
    server = WebServer()
    server.serve()
