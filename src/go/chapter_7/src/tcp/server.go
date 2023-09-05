package tcp

import (
	"fmt"
	"log"
	"net"
	"os"
)

type Server struct{}

func (server Server) Serve() error {
	log.Print("=== サーバーを起動します ===")

	ln, err := net.Listen("tcp", ":8080")
	if err != nil {
		fmt.Printf("failed to listen: %s\n", err)
		return err
	}

	log.Print("=== クライアントからの接続を待ちます ===")
	// Acceptはブロッキング処理
	// clientとの接続が確立されたコネクションインスタンスが返される
	clientConn, err := ln.Accept()
	if err != nil {
		fmt.Printf("failed to accept: %s\n", err)
		return err
	}
	// TCP通信を終了するときはcloseをする」という習慣をつけておく
	defer clientConn.Close()

	log.Printf("=== クライアントとの接続が完了しました。 remote_address: %s\n", clientConn.RemoteAddr().String())
	log.Printf("=== クライアントとの接続が完了しました。 local_address: %s\n", clientConn.LocalAddr().String())

	buf := make([]byte, 1024)

	// Readもおそらくブロッキング処理
	requestBytesSize, err := clientConn.Read(buf)
	if err != nil {
		fmt.Printf("failed to read: %s\n", err.Error())
		return err
	}

	// 0から始まる数字は8進数
	// umaskがデフォルトで022だから、ファイルのパーミッションは0644(rw--r--r--)になる
	// umaskはumaskコマンドで確認できる
	err = os.WriteFile("http_messages/server_recv_from_chrome.txt", buf[:requestBytesSize], 0666)
	if err != nil {
		fmt.Printf("failed to read: %s\n", err.Error())
		return err
	}

	return nil
}
