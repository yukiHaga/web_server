package main

import (
	"github.com/yukiHaga/web_server/src/pkg/henagin/server"
)

func main() {
	webServer := server.Server{}
	webServer.Serve()

	// tcpClient := tcp.Client{}
	// err := tcpClient.Request()
	// if err != nil {
	// 	log.Println("=== サーバーを停止します ===")
	// }
}
