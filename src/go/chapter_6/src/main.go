package main

import (
	"github.com/yukiHaga/web_server/src/tcp"
)

func main() {
	tcpServer := tcp.Server{}
	err := tcpServer.Serve()
	if err != nil {
		print("=== サーバーを停止します ===")
	}
}
