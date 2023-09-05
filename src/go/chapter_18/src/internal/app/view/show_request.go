package view

import "fmt"

func ShowRequest(method, targetPath, httpVersion, headers, body string) string {
	return fmt.Sprintf(
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
		headers,
		body,
	)
}
