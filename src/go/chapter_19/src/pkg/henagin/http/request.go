package http

type Request struct {
	Method      string
	TargetPath  string
	HttpVersion string
	Headers     map[string]string
	Body        []byte
	Params      map[string]string
}

func NewRequest(method string, targetPath string, httpVersion string, headers map[string]string, body []byte) *Request {
	return &Request{
		Method:      method,
		TargetPath:  targetPath,
		HttpVersion: httpVersion,
		Headers:     headers,
		Body:        body,
		Params:      map[string]string{},
	}
}
