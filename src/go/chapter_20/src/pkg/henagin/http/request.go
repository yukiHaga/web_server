package http

import (
	"fmt"
	"regexp"
)

type Request struct {
	Method      string
	TargetPath  string
	HttpVersion string
	Headers     map[string]string
	Body        []byte
	Cookies     map[string]*Cookie
	Params      map[string]string
}

func NewRequest(method string, targetPath string, httpVersion string, headers map[string]string, body []byte) *Request {
	cookies := getCookiesByHeaders(headers)
	return &Request{
		Method:      method,
		TargetPath:  targetPath,
		HttpVersion: httpVersion,
		Headers:     headers,
		Body:        body,
		Cookies:     cookies,
		Params:      map[string]string{},
	}
}

func getCookiesByHeaders(headers map[string]string) map[string]*Cookie {
	cookies := map[string]*Cookie{}
	if value, isThere := headers["Cookie"]; isThere {
		re := regexp.MustCompile("; ")
		cookiePairs := re.Split(value, -1)
		for _, cookiePair := range cookiePairs {
			re := regexp.MustCompile("=")
			splitCookiePair := re.Split(cookiePair, -1)
			name := splitCookiePair[0]
			value := splitCookiePair[1]
			cookies[name] = NewCookie(name, value)
		}
	}

	fmt.Println("cookies", cookies)

	return cookies
}

func (request *Request) GetCookieByName(name string) (*Cookie, bool) {
	cookie, isThere := request.Cookies[name]
	return cookie, isThere
}
