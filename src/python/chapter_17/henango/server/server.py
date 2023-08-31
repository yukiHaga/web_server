import socket
from henango.server.worker import Worker

# Webサーバーを表すクラス


class Server:
    # サーバーを起動する
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

                # クライアントを処理スレッドを作成
                # コネクションを確立したクライアントを処理する スレッド を作成し、スレッドの処理を開始させます。
                # 前回まで.handle_client()というメソッドで行っていた処理と、前後の例外処理は全てこのスレッド内の処理にお引越ししました。
                # スレッドとはコンピュータが並列に処理を行うことが可能な処理系列のこと
                thread = Worker(client_socket, address)
                thread.start()

        finally:
            print("===サーバーを停止します。===")

    def create_server_socket(self) -> socket:
        server_socket = socket.socket()
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # socketをlocalhostのポート8080番に割り当てる
        server_socket.bind(("localhost", 8080))
        server_socket.listen(10)
        return server_socket
