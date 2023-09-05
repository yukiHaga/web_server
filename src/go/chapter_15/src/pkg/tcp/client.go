package tcp

import (
	"log"
	"net"
	"os"
)

type Client struct{}

func (client Client) Request() error {
	log.Println("=== クライアントを起動します ===")
	log.Println("=== サーバーと接続します ===")
	clientConn, err := net.Dial("tcp", "localhost:80")
	log.Println("==== サーバーと接続が完了しました ===")
	if err != nil {
		log.Printf("fail to connection: %v\n", err)
		return err
	}
	defer clientConn.Close()

	// サーバーに送信するリクエストを、ファイルから取得する
	bytes, err := os.ReadFile("http_messages/server_recv_from_chrome.txt")
	if err != nil {
		log.Printf("fail to read file: %v\n", err)
		return err
	}

	// これもおそらくブロッキング処理
	// リクエストを送信している
	_, err = clientConn.Write(bytes)
	if err != nil {
		log.Printf("fail to write: %v\n", err)
		return err
	}

	buf := make([]byte, 1024)

	// サーバーからのレスポンスを取得する
	receivedBytesSize, err := clientConn.Read(buf)
	if err != nil {
		log.Printf("fail to read: %v\n", err)
		return err
	}

	// レスポンスの内容をファイルに書き出す
	err = os.WriteFile("http_messages/client_recv_from_apache.txt", buf[:receivedBytesSize], 0666)
	if err != nil {
		log.Printf("fail to write file: %v\n", err)
		return err
	}

	return nil
}
