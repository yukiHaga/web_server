package web

import (
	"bytes"
	"fmt"
	"log"
	"net"
	"net/url"
	"os"
	"path"
	"regexp"
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
		fmt.Printf("fail to get static root: %s\n", err)
		return err
	}

	buf := make([]byte, 1024)

	// Readもおそらくブロッキング処理
	requestBytesSize, err := clientConn.Read(buf)
	if err != nil {
		fmt.Printf("fail to read: %s\n", err)
		return err
	}

	// リクエストを解析する
	// ターゲットを取得したい
	method, targetPath, httpVersion, headers, bodyBytes := parseRequest(buf[:requestBytesSize])
	fmt.Println(targetPath)

	// レスポンスの生成
	statusLine := "HTTP/1.1 200 OK\r\n"

	// パスに応じてレスポンスボディが変化するので、事前に変数として定義した
	var responseBodyBytes []byte
	if targetPath == "/now" {
		t := time.Now()
		responseBodyBytes = []byte(fmt.Sprintf(
			`<!doctype html>
			<html lang="ja">
			<head>
			  <meta charset="UTF-8">
			  <title>HenaServer: now</title>
			</head>
			<body>
			  <h1>now: %v</h1>
			</body>
			</html>`,
			timeutil.Strftime(&t, "%a, %d %b %Y %H:%M:%S"),
		))
	} else if targetPath == "/show_request" {
		fmt.Println(string(bodyBytes))
		responseBodyBytes = []byte(fmt.Sprintf(
			`<!doctype html>
			<html lang="ja">
			<head>
			  <meta charset="UTF-8">
			  <title>HenaServer: now</title>
			</head>
			<body>
			  <h1>RequestLine:</h1>
			  <pre>%s %s %s</pre>
			  <h1>RequestHeader:</h1>
			  <pre>%s</pre>
			  <h1>RequestBody:</h1>
			  <p>%s</p>
			</body>
			</html>`,
			method,
			targetPath,
			httpVersion,
			PFormatForHeader(headers),
			string(bodyBytes),
		))
	} else if targetPath == "/parameters" {
		if method == "GET" {
			responseBodyBytes, _ = os.ReadFile(path.Join(STATIC_ROOT, "405.html"))
			statusLine = "HTTP/1.1 405 Method Not Allowed\r\n"
		} else if method == "POST" {
			// 多分ファイルの変換処理でミスっているかも
			postParams, err := url.ParseQuery(string(bodyBytes))
			if err != nil {
				fmt.Printf("fail to parse post params: %v\n", err)
				return err
			}

			formatedPostParams := ""
			for key, value := range postParams {
				formatedPostParams += fmt.Sprintf("%s: %v\r\n", key, value)
			}

			responseBodyBytes = []byte(fmt.Sprintf(
				`<!doctype html>
				<html lang="ja">
				<head>
				<meta charset="UTF-8">
				<title>HenaServer: now</title>
				</head>
				<body>
				<h1>PostParams:</h1>
				<pre>%s</pre>
				</body>
				</html>`,
				formatedPostParams,
			))
		}
	} else {
		responseBodyBytes, err = getStaticFile(targetPath)
		if err != nil {
			fmt.Println("fail to read file:", err)
			statusLine = "HTTP/1.1 404 Not Found\r\n"
			responseBodyBytes, _ = os.ReadFile(path.Join(STATIC_ROOT, "404.html"))
		}
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

// ヘッダーはUTF-8でエンコードされた文字列だと決まっているのですが、
// ボディは画像やPDFなど、文字列ではなくバイナリデータが送られてくる可能性があるため、常に文字列に変換できるとは限らないのです。
// なので、ボディは中身が文字列だと分かっている場合しか文字列に変換してはいけないのです。
func parseRequest(requestBytes []byte) (string, string, string, map[string]string, []byte) {
	// HTTPメッセージを安易にstringに変換してはダメ。バイナリのままsplitする

	// requestMessage := string(requestBytes)
	// // nは返す部分文字列の数を決める
	// requestLine := strings.SplitN(requestMessage, "\r\n", 2)[0]
	// spritRequestLine := strings.SplitN(requestLine, " ", 3)
	// method := spritRequestLine[0]
	// targetPath := spritRequestLine[1]
	// httpVersion := spritRequestLine[2]

	// headerAndBody := strings.SplitN(requestMessage, "\r\n", 2)[1]
	// splitHeaderAndBody := strings.SplitN(headerAndBody, "\r\n\r\n", 2)
	// header := splitHeaderAndBody[0]
	// body := splitHeaderAndBody[1]

	// return method, targetPath, httpVersion, header, body

	// 一回で読み込める量に限界があるのかも
	if err := os.WriteFile("http_messages/server_recv_from_form", requestBytes, os.ModePerm); err != nil {
		log.Printf("fail to write file: %v\r\n", err)
	}

	// バイナリのままsplitsする
	requestLineAndremainBytes := bytes.SplitN(requestBytes, []byte("\r\n"), 2)
	requestLine := string(requestLineAndremainBytes[0])
	remainBytes := requestLineAndremainBytes[1]
	headerAndBodyBytes := bytes.SplitN(remainBytes, []byte("\r\n\r\n"), 2)
	headerBytes := headerAndBodyBytes[0]
	bodyBytes := headerAndBodyBytes[1]

	// リクエストラインをさらに分解する
	splitRequestLine := strings.SplitN(requestLine, " ", 3)
	method := splitRequestLine[0]
	targetPath := splitRequestLine[1]
	httpVersion := splitRequestLine[2]

	// ヘッダーを扱いやすいようにマップ型に変換しておく
	headers := map[string]string{}

	for _, v := range strings.Split(string(headerBytes), "\r\n") {
		// 正規表現を生成(Goには正規表現リテラルがないくさい)
		re := regexp.MustCompile(": *")
		keyAndValue := re.Split(v, 2)
		key := keyAndValue[0]
		value := keyAndValue[1]
		headers[key] = value
	}

	return method, targetPath, httpVersion, headers, bodyBytes
}

// lstripの処理は何の目的で行われているのか、その目的を関数やメソッドにする
func getStaticFile(targetPath string) ([]byte, error) {
	STATIC_ROOT, err := constants.GetStaticRoot()
	if err != nil {
		fmt.Printf("fail to get static root: %s\n", err)
		return nil, err
	}

	targetFile := strings.TrimPrefix(targetPath, "/")
	responseBodyBytes, err := os.ReadFile(path.Join(STATIC_ROOT, targetFile))
	if err != nil {
		fmt.Printf("fail to read file: %s\n", err)
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

	if ext != "" {
		value, isThere := constants.MIME_TYPES[ext]
		if isThere {
			responseHeader += fmt.Sprintf("Content-Type: %v; charset=UTF-8\r\n", value)
		} else {
			// 知らない対応していない拡張子の場合はoctet-streamとする
			responseHeader += "Content-Type: application/octet-stream; charset=UTF-8\r\n"
		}
	} else {
		responseHeader += "Content-Type: text/html; charset=UTF-8\r\n"
	}

	return responseHeader
}
