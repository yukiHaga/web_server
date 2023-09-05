package controller

import "github.com/yukiHaga/web_server/src/pkg/http"

type Controller func(*http.Request) *http.Response
