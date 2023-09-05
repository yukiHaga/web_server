package web

import (
	"bytes"
	"fmt"
	"log"
	"net"
	"os"
	"path"
	"regexp"
	"strings"
	"time"

	"github.com/yukiHaga/web_server/src/pkg/constants"
	"github.com/yukiHaga/web_server/src/pkg/http"
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
	STATIC_ROOT, _ := constants.GetStaticRoot()
	buf := make([]byte, 1024)

	// Readもおそらくブロッキング処理
	requestBytesSize, err := clientConn.Read(buf)
	if err != nil {
		fmt.Printf("fail to read: %s\n", err)
		return err
	}

	// リクエストを解析する
	// ターゲットを取得したい
	method, targetPath, httpVersion, headers, body := parseRequest(buf[:requestBytesSize])
	request := http.NewRequest(method, targetPath, httpVersion, headers, body)
	fmt.Println(targetPath)

	// パスに応じてレスポンスボディが変化するので、事前に変数として定義した
	response := &http.Response{}
	var statusCode string
	var statusReasonPhrase string

	if _, isThere := UrlController[targetPath]; isThere {
		controller := UrlController[targetPath]
		response = controller(request)
	} else {
		responseBody, err := getStaticFile(targetPath)
		response = http.NewResponse(
			http.VersionsFor11,
			http.StatusSuccessCode,
			http.StatusReasonOk,
			request.TargetPath,
			responseBody,
		)
		if err != nil {
			fmt.Println("fail to read file:", err)
			statusCode = http.StatusNotFoundCode
			statusReasonPhrase = http.StatusReasonNotFound
			responseBody, _ = os.ReadFile(path.Join(STATIC_ROOT, "404.html"))
			response = http.NewResponse(
				http.VersionsFor11,
				statusCode,
				statusReasonPhrase,
				request.TargetPath,
				responseBody,
			)
		}

	}

	responseMessage := response.BuildMessage()

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

	// 一回で読み込める量に限界があるのかも
	if err := os.WriteFile("http_messages/server_recv_from_form", requestBytes, os.ModePerm); err != nil {
		log.Printf("fail to write file: %v\r\n", err)
	}

	// バイナリのままsplitsする
	requestLineAndremainBytes := bytes.SplitN(requestBytes, []byte("\r\n"), 2)
	requestLine := string(requestLineAndremainBytes[0])
	remainBytes := requestLineAndremainBytes[1]
	headerAndBody := bytes.SplitN(remainBytes, []byte("\r\n\r\n"), 2)
	headerBytes := headerAndBody[0]
	body := headerAndBody[1]

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

	return method, targetPath, httpVersion, headers, body
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
