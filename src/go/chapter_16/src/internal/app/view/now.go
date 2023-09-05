package view

import (
	"fmt"
)

func Now(time string) string {
	return fmt.Sprintf(
		`<!doctype html>
		<html lang="ja">
		<head>
		  <meta charset="UTF-8">
		  <title>HenaServer: now</title>
		</head>
		<body>
		  <h1>now: %v</h1>
		</body>
		</html>`,
		time,
	)
}
