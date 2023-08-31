import socket

# TCP通信を行うクライアントを表すクラス
class TCPClient:
    def request(self):
        print("===クライアントを起動します===")

        try:
            client_socket = socket.socket()
            client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            print("===サーバーと接続します===")
            # Apatchが起動しているはずのポートへ向けて接続を試みている
            client_socket.connect(("127.0.0.1", 80))
            print("===サーバーとの接続が完了しました===")

            # サーバに送信するリクエストを、ファイルから取得する
            with open("client_send.txt", "rb") as f:
                request = f.read()

            # サーバーへリクエストを送信する
            client_socket.send(request)

            # サーバーからレスポンスが送られてくるのを待ち、取得する
            # これもブロッキング処理なのか。
            # サーバーはすぐにレスポンスを返すとはいえ、ほんの少しはタイムラグがあります。
            # .send()をした直後はまだサーバーがレスポンスを返していませんので、.recv()メソッドが実行された時点ではまだネットワークバッファには受け取りデータが溜まっていない状態です。
            # ですので、プログラムはここで一瞬止まり、レスポンスを待つことになります。
            # （おさらいですが、.recv()メソッドは呼び出した時点ですでにネットワークバッファにデータが溜まっていれば値を返しますが、データが空っぽのときは新しいデータが届くまでプログラムを停止させます。）
            response = client_socket.recv(4096)

            # レスポンスの内容をファイルに書き出す
            with open("client_recv.txt", "wb") as f:
                f.write(response)

            # 通信を終了する
            # python にはコンテキストマネージャー（with 句）というものが用意されており、file の close や、socket の close のような忘れてはいけない処理を
            # 自動的にやってくれる仕組みがあります。
            # socket ライブラリもそれに対応しており、以下の記法を使うと with 句を抜ける際に自動的に close を実行してくれます。
            client_socket.close()

        finally:
            print("===クライアントを停止します===")

if __name__ == "__main__":
    client = TCPClient()
    client.request()
