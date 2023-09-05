package web

import (
	"log"
	"net"
)

type Server struct{}

// 自作Webサーバー
// 銅的に生成したHTMLを返せるようにした
func (server Server) Serve() {
	log.Print("=== Server: サーバーを起動します ===")

	ln, err := net.Listen("tcp", ":8080")
	if err != nil {
		log.Printf("fail to listen: %v\n", err)
		log.Println("=== Server: サーバーを停止します ===")
		return
	}

	for {
		log.Print("=== Server: クライアントからの接続を待ちます ===")
		// Acceptはブロッキング処理
		// clientとの接続が確立されたコネクションインスタンスが返される
		clientConn, err := ln.Accept()
		if err != nil {
			log.Printf("fail to accept: %v\n", err)
			log.Println("=== Server: サーバーを停止します ===")
			return
		}

		log.Printf("=== Server: クライアントとの接続が完了しました。 remote_address: %s\n", clientConn.RemoteAddr().String())

		thread := WorkerThread{clientConn: clientConn, clientAddress: clientConn.RemoteAddr().String()}
		thread.Run()
	}
}
