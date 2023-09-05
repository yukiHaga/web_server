package main

import (
	"log"

	"github.com/yukiHaga/web_server/src/pkg/web"
)

func main() {
	webServer := web.Server{}
	err := webServer.Serve()
	if err != nil {
		log.Println("=== サーバーを停止します ===")
	}

	// tcpClient := tcp.Client{}
	// err := tcpClient.Request()
	// if err != nil {
	// 	log.Println("=== サーバーを停止します ===")
	// }
}
