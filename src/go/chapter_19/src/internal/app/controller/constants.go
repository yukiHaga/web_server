package controller

import "github.com/yukiHaga/web_server/src/pkg/henagin/http"

type Controller interface {
	Action(request *http.Request) *http.Response
}
