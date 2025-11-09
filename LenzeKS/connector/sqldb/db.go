package sqldb

type Database interface {
	Connect() error
	Close() error
}
