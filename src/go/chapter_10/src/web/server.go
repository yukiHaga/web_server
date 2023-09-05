package web

import (
	"fmt"
	"log"
	"net"
	"os"
	"time"

	"github.com/leekchan/timeutil"
)

type Server struct{}

// 自作Webサーバー ver0.2
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
		fmt.Printf("failed to write: %s\n", err.Error())
		return err
	}

	statusLine := "HTTP/1.1 200 OK\r\n"
	responseBody := "<html><body><h1>It Go Go works!</h1></body></html>\r\n"
	t := time.Now()
	responseHeader := fmt.Sprintf("Date: %v\r\n", timeutil.Strftime(&t, "%a, %d %b %Y %H:%M:%S"))
	responseHeader += "Server: HenaGoServer/0.1\r\n"
	responseHeader += fmt.Sprintf("Content-Length: %v\r\n", len([]byte(responseBody)))
	responseHeader += "Connection: Close\r\n"
	responseHeader += "Content-Type: text/html\r\n"

	responseMessage := statusLine + responseHeader + "\r\n" + responseBody

	// Writeもおそらくブロッキング処理
	_, err = clientConn.Write([]byte(responseMessage))
	if err != nil {
		fmt.Printf("failed to write: %s\n", err.Error())
		return err
	}

	return nil
}
