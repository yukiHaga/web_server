package view

import "fmt"

func Parameters(formatedPostParams string) string {
	return fmt.Sprintf(
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
	)
}
