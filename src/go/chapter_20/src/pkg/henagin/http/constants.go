package http

const (
	Get  = "GET"
	Post = "POST"
)

const VersionsFor11 = "HTTP/1.1"

const (
	StatusSuccessCode             = "200"
	StatusRedirectCode            = "302"
	StatusNotFoundCode            = "404"
	StatusMethodNotAllowedCode    = "405"
	StatusInternalServerErrorCode = "500"
)

const (
	StatusReasonOk                  = "OK"
	StatusReasonRedirect            = "Found"
	StatusReasonNotFound            = "Not Found"
	StatusReasonMethodNotAllowed    = "Method Not Allowed"
	StatusReasonInternalServerError = "Internal Server Error"
)
