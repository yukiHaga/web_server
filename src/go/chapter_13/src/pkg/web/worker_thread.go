package web

import (
	"fmt"
	"log"
	"net"
	"os"
	"path"
	"strings"
	"time"

	"github.com/leekchan/timeutil"
	"github.com/yukiHaga/web_server/src/pkg/constants"
)

type WorkerThread struct {
	clientConn    net.Conn
	clientAddress string
}

func (thread WorkerThread) Run() {
	go func() {
		err := handleClient(thread.clientConn)
		defer func() {
			// TCP通信を終了するときはcloseをする」という習慣をつけておく
			thread.clientConn.Close()
		}()

		if err != nil {
			log.Printf("failed to handle client: %s\n", err.Error())
			log.Printf("=== Worker: リクエストの処理中にエラーが発生しました ===")
			return
		}
		time.Sleep(time.Second * 10)
		log.Printf("=== Worker: クライアントとの通信を終了します remote_address: %v", thread.clientAddress)
	}()
}

// クライアントからのリクエストを処理するときに、毎回手続き書くのだるいから関数にした。
// あと手続きがばーっと書いてあるより抽象化されているほうがわかりやすい。どう抽象化するのかが大事。手続き的に書くことで、見にいく必要がないっていうメリットもある
// 意味のあるまとまり単位(手続きでばーっと書かれてたらわか離にくいやつ)、再利用する単位でメソッド関数化する。これ抽象化してもどうせ見に行くな、手続き的に書いてあるほうがわかりやすいってやつは手続き的に書いたほうが良いかも(おそらくへんな単位で抽象化しているかも)。
func handleClient(clientConn net.Conn) error {
	STATIC_ROOT, err := constants.GetStaticRoot()
	if err != nil {
		fmt.Printf("failed to get static root: %s\n", err)
		return err
	}

	buf := make([]byte, 1024)

	// Readもおそらくブロッキング処理
	requestBytesSize, err := clientConn.Read(buf)
	if err != nil {
		fmt.Printf("failed to read: %s\n", err.Error())
		return err
	}

	// リクエストを解析する
	// ターゲットを取得したい
	_, targetPath, _ := parseRequest(buf[:requestBytesSize])
	fmt.Println(targetPath)

	// レスポンスの生成
	statusLine := "HTTP/1.1 200 OK\r\n"
	responseBodyBytes, err := getStaticFile(targetPath)
	if err != nil {
		fmt.Println("fail to read file:", err)
		statusLine = "HTTP/1.1 404 Not Found"
		responseBodyBytes, _ = os.ReadFile(path.Join(STATIC_ROOT, "404.html"))
	}

	responseHeader := buildResponseHeader(targetPath, responseBodyBytes)
	responseMessage := (statusLine + responseHeader + "\r\n") + string(responseBodyBytes)

	// Writeもおそらくブロッキング処理
	_, err = clientConn.Write([]byte(responseMessage))
	if err != nil {
		fmt.Println("fail to write", err)
		return err
	}
	return nil
}

func parseRequest(requestBytes []byte) (string, string, string) {
	requestMessage := string(requestBytes)
	// nは返す部分文字列の数を決める
	requestLine := strings.SplitN(requestMessage, "\r\n", 2)[0]
	spritRequestLine := strings.SplitN(requestLine, " ", 3)
	method := spritRequestLine[0]
	targetPath := spritRequestLine[1]
	httpVersion := spritRequestLine[2]

	return method, targetPath, httpVersion
}

// lstripの処理は何の目的で行われているのか、その目的を関数やメソッドにする
func getStaticFile(targetPath string) ([]byte, error) {
	STATIC_ROOT, err := constants.GetStaticRoot()
	if err != nil {
		fmt.Printf("failed to get static root: %s\n", err)
		return nil, err
	}

	targetFile := strings.TrimPrefix(targetPath, "/")
	responseBodyBytes, err := os.ReadFile(path.Join(STATIC_ROOT, targetFile))
	if err != nil {
		fmt.Printf("failed to read file: %s\n", err)
		return nil, err
	}
	return responseBodyBytes, nil
}

func buildResponseHeader(targetPath string, responseBodyBytes []byte) string {
	var ext string
	if strings.Contains(targetPath, ".") {
		ext = strings.SplitN(targetPath, ".", 2)[1]
	} else {
		ext = ""
	}

	t := time.Now()
	responseHeader := fmt.Sprintf("Date: %v\r\n", timeutil.Strftime(&t, "%a, %d %b %Y %H:%M:%S"))
	responseHeader += "Server: HenaGoServer/0.1\r\n"
	responseHeader += fmt.Sprintf("Content-Length: %v\r\n", len(responseBodyBytes))
	responseHeader += "Connection: Close\r\n"

	value, isThere := constants.MIME_TYPES[ext]
	if isThere {
		responseHeader += fmt.Sprintf("Content-Type: %v\r\n", value)
	} else {
		// 知らない対応していない拡張子の場合はoctet-streamとする
		responseHeader += "Content-Type: application/octet-stream\r\n"
	}

	return responseHeader
}
