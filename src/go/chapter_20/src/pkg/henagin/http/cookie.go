package http

type Cookie struct {
	Name  string
	Value string
	// Expires time.Time
	// Domain   string
	// Path     string
	HttpOnly bool
}

func NewCookie(
	name string,
	value string,
	// expires time.Time,
	// domain string,
	// path string,
	// httpOnly bool,
) *Cookie {
	return &Cookie{
		Name:  name,
		Value: value,
		// Domain:   domain,
		// Path:     path,
		HttpOnly: true,
	}
}
