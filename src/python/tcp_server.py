import socket

# TCP通信を行うサーバークラス
class TCPServer:
    # サーバーを起動する
    def serve(self):
        print("===サーバーを起動します===")

        try:
            server_socket = socket.socket()
            # このコードは、特にソケットをバインドする際に役立ちます。通常、TCPサーバーソケットをバインドする際、
            # 前回のセッションからのTIME_WAIT状態を回避するために、SO_REUSEADDRオプションを有効にすることがあります。
            # これにより、アドレスが再利用され、再起動後すぐに同じアドレスでソケットをバインドすることができます。
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # bindした時点でまだポートを占有しているわけではない。listenをしてからバインドしたポートば占有される
            server_socket.bind(("localhost", 8080))
            # listenの引数の10は、このサーバーがいくつのクライアントと同時に通信を行えるかを制限する数字である。
            server_socket.listen(10)

            # 外部からの接続を待ち、接続があったらコネクションを確立する
            print("=== クライアントからの接続を待ちます ===")
            # acceptはブロッキングな処理（プログラムを停止させる処理）
            # クライアントからの通信がきたら、コネクションが確立される
            # サーバー側のソケットは次の接続を待たないといけないから、サーバーが生成したクライアント側のソケットにクライアントへの送信処理を委譲する
            # client_socketは、クライアントとの接続が確立された新しいsocketインスタンス
            (client_socket, address) = server_socket.accept()
            print(f"=== クライアントとの接続が完了しました remote_address: {address} ===")

            # クライアントから送られてきたデータを取得する
            # bytes型で取得する
            # recvメソッドは、acceptメソッドと同様に、すでにクライアントが送ってきたデータが溜まっていればそれを直ちに全て取得しますが、
            # 溜まっていなければプログラムは停止してデータが新しく送られてくるのを待ってしまう
            # 引数に与えるintはネットワークバッファ（到着したデータをためておくところ）から一回で取得するバイト数を表しており、例えば4096を指定すると4096バイトずつデータを取得します。
            # 今回のケースでは、ブラウザはコネクションが確立すると直ちにメッセージを送って来ますので、このrecv()はほとんど待たされることはなくすぐに処理が完了し、データを受け取ることができます。
            request = client_socket.recv(4096)

            # with構文を使えば、close関数を呼び出す手間を省ける
            # # クライアントから送られてきたデータをファイルに書き出す
            with open("server_recv.txt", "wb") as f:
                f.write(request)

            # 返事は特に返さず、通信を終了させる
            client_socket.close()

        # 実行中に例外が出た場合も、出なかった場合も、最後にはサーバーの終了ログをコンソールに出してから処理を終了する。
        # finallyは、「例外が発生したとしても発生しなかったとしても実行したい処理」を書くために使います。
        finally:
            print("=== サーバーを停止します。 ===")

if __name__ == '__main__':
    server = TCPServer()
    server.serve()


