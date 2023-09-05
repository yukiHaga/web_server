package web

import (
	"fmt"
	"log"
	"net"
	"os"
	"path"
	"path/filepath"
	"strings"
	"time"

	"github.com/leekchan/timeutil"
)

type Server struct{}

// 自作Webサーバー ver0.4
// 複数回のHTTPリクエストに対応できるようになった
func (server Server) Serve() {
	log.Print("=== サーバーを起動します ===")

	ln, err := net.Listen("tcp", ":8080")
	if err != nil {
		fmt.Printf("failed to listen: %s\n", err)
		log.Println("=== サーバーを停止します ===")
	}

	// カレントディレクトリの取得
	currentDir, err := os.Getwd()
	if err != nil {
		fmt.Println("カレントディレクトリを取得できませんでした:", err)
		log.Println("=== サーバーを停止します ===")
		return
	}

	// 絶対パスの取得
	BASE_DIR, err := filepath.Abs(currentDir)
	if err != nil {
		fmt.Println("絶対パスを取得できませんでした:", err)
		log.Println("=== サーバーを停止します ===")
		return
	}

	// 拡張子とMIME Typeの対応
	MIME_TYPES := map[string]string{
		"html": "text/html",
		"css":  "text/css",
		"png":  "image/png",
		"jpg":  "image/jpg",
		"gif":  "image/gif",
	}

	STATIC_ROOT := path.Join(BASE_DIR, "src", "static")

	for {
		log.Print("=== クライアントからの接続を待ちます ===")
		// Acceptはブロッキング処理
		// clientとの接続が確立されたコネクションインスタンスが返される
		clientConn, err := ln.Accept()
		if err != nil {
			fmt.Printf("failed to accept: %s\n", err)
			log.Println("=== サーバーを停止します ===")
			return
		}

		log.Printf("=== クライアントとの接続が完了しました。 remote_address: %s\n", clientConn.RemoteAddr().String())
		log.Printf("=== クライアントとの接続が完了しました。 local_address: %s\n", clientConn.LocalAddr().String())

		buf := make([]byte, 1024)

		// Readもおそらくブロッキング処理
		requestBytesSize, err := clientConn.Read(buf)
		if err != nil {
			fmt.Printf("failed to read: %s\n", err.Error())
			log.Println("=== サーバーを停止します ===")
			return
		}

		// リクエストを解析する
		// ターゲットを取得したい
		requestMessage := string(buf[:requestBytesSize])
		// nは返す部分文字列の数を決める
		requestLine := strings.SplitN(requestMessage, "\r\n", 2)[0]
		targetPath := strings.SplitN(requestLine, " ", 3)[1]
		log.Println(targetPath)
		targetFile := strings.TrimPrefix(targetPath, "/")

		var ext string
		if strings.Contains(targetFile, ".") {
			ext = strings.SplitN(targetFile, ".", 2)[1]
		} else {
			ext = ""
		}

		// レスポンスの生成
		statusLine := "HTTP/1.1 200 OK\r\n"
		responseBodyBytes, err := os.ReadFile(path.Join(STATIC_ROOT, targetFile))
		if err != nil {
			fmt.Println("fail to read file:", err)
			statusLine = "HTTP/1.1 404 Not Found"
			responseBodyBytes, _ = os.ReadFile(path.Join(STATIC_ROOT, "404.html"))
		}

		t := time.Now()
		responseHeader := fmt.Sprintf("Date: %v\r\n", timeutil.Strftime(&t, "%a, %d %b %Y %H:%M:%S"))
		responseHeader += "Server: HenaGoServer/0.1\r\n"
		responseHeader += fmt.Sprintf("Content-Length: %v\r\n", len(responseBodyBytes))
		responseHeader += "Connection: Close\r\n"

		value, isThere := MIME_TYPES[ext]
		if isThere {
			responseHeader += fmt.Sprintf("Content-Type: %v\r\n", value)
		} else {
			// 知らない対応していない拡張子の場合はoctet-streamとする
			responseHeader += "Content-Type: application/octet-stream\r\n"
		}

		responseMessage := (statusLine + responseHeader + "\r\n") + string(responseBodyBytes)

		// Writeもおそらくブロッキング処理
		_, err = clientConn.Write([]byte(responseMessage))
		if err != nil {
			fmt.Printf("failed to write: %s\n", err.Error())
			log.Println("=== サーバーを停止します ===")
			return
		}

		// TCP通信を終了するときはcloseをする」という習慣をつけておく
		clientConn.Close()
	}
}
