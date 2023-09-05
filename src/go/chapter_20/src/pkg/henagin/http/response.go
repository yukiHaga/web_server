package http

import (
	"fmt"
	"regexp"
	"strings"
	"time"

	"github.com/leekchan/timeutil"
	"github.com/yukiHaga/web_server/src/pkg/henagin/constants"
)

type Response struct {
	HttpVersion  string
	StatusCode   string
	ReasonPhrase string
	Headers      []*Header
	Body         []byte
}

func NewResponse(httpVersion string, statusCode string, reasonPhrase string, targetPath string, body []byte) *Response {
	return &Response{
		HttpVersion:  httpVersion,
		StatusCode:   statusCode,
		ReasonPhrase: reasonPhrase,
		Headers:      buildResponseHeaders(targetPath, body),
		Body:         body,
	}
}

func buildResponseHeaders(targetPath string, body []byte) []*Header {
	var ext string
	if strings.Contains(targetPath, ".") {
		ext = strings.SplitN(targetPath, ".", 2)[1]
	} else {
		ext = ""
	}

	t := time.Now()
	responseHeader := fmt.Sprintf("Date: %v\r\n", timeutil.Strftime(&t, "%a, %d %b %Y %H:%M:%S"))
	responseHeader += "Server: HenaGoServer/0.1\r\n"
	responseHeader += fmt.Sprintf("Content-Length: %v\r\n", len(body))
	if ext != "" {
		value, isThere := constants.MIME_TYPES[ext]
		if isThere {
			if value == constants.MIME_TYPES["html"] {
				responseHeader += fmt.Sprintf("Content-Type: %v; charset=UTF-8\r\n", value)
			} else {
				responseHeader += fmt.Sprintf("Content-Type: %v\r\n", value)
			}
		} else {
			// 知らない対応していない拡張子の場合はoctet-streamとする
			responseHeader += "Content-Type: application/octet-stream; charset=UTF-8\r\n"
		}
	} else {
		responseHeader += "Content-Type: text/html; charset=UTF-8\r\n"
	}

	responseHeader += "Connection: Close\r\n"

	headers := []*Header{}
	for _, v := range strings.Split(strings.TrimSuffix(responseHeader, "\r\n"), "\r\n") {
		// 正規表現を生成(Goには正規表現リテラルがないくさい)
		re := regexp.MustCompile(": *")
		nameAndValue := re.Split(v, 2)
		name := nameAndValue[0]
		value := nameAndValue[1]
		headers = append(headers, NewHeader(name, value))
	}

	return headers
}

func (response *Response) BuildMessage() string {
	statusLine := fmt.Sprintf("%s %s %s\r\n", response.HttpVersion, response.StatusCode, response.ReasonPhrase)
	responseHeader := response.ConvertToStringHeader()
	responseMessage := (statusLine + responseHeader + "\r\n") + string(response.Body)

	return responseMessage
}

func (response *Response) ConvertToStringHeader() string {
	stringHeader := ""
	for _, header := range response.Headers {
		stringHeader += fmt.Sprintf("%s: %s\r\n", header.Name, header.Value)
	}

	return stringHeader
}

func (response *Response) SetHeader(name, value string) {
	response.Headers = append(response.Headers, NewHeader(name, value))
}

func (response *Response) SetCookieHeader(value string) {
	value = fmt.Sprintf("%s; %s", value, "HttpOnly")
	response.SetHeader("Set-Cookie", value)
}
