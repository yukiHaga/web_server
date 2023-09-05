package main

import (
	"log"

	"github.com/yukiHaga/web_server/src/tcp"
)

func main() {
	tcpServer := tcp.Server{}
	err := tcpServer.Serve()
	if err != nil {
		log.Println("=== サーバーを停止します ===")
	}

	// tcpClient := tcp.Client{}
	// err := tcpClient.Request()
	// if err != nil {
	// 	log.Println("=== サーバーを停止します ===")
	// }
}
