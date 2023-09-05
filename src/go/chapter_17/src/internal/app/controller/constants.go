package controller

import "github.com/yukiHaga/web_server/src/pkg/henagin/http"

type Controller func(*http.Request) *http.Response
