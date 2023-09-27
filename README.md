# Proteus Command Line Client

A simple command line client to modify DNS entries in Proteus.

## Installation

Use `pip` to install `proteuscmd`:

```
❯ pip install proteuscmd
```

## Configuration

Configure access credentials in `~/.proteus.json`:
```json
{
	"user": "api-user",
	"password": "super.secret!",
	"url": "https://proteus.example.com"
}
```

Additionally, you can specify a map of automatic replacements for domains.
This can be useful if, for example, all your domains also have an alternate domain with a `DNAME` record.
```json
{
	...
	"replace": {
		".ex.com": ".example.com"
	}
}
```

## Usage

```
❯ proteuscmd
Usage: python -m proteuscmd [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  dns  Get information about or update DNS entries.
  ip   Register IP addresses.
```

Get information about a DNS record:
```
❯ proteuscmd dns get lktest.uni-osnabrueck.de
```

Set an alias record:
```
❯ proteuscmd dns set lktest.uni-osnabrueck.de vm123.rz.uni-osnabrueck.de
```

Set a host record:
```
❯ proteuscmd dns set lktest.uni-osnabrueck.de 131.12.65.123
```

Delete a record:
```
❯ proteuscmd dns delete lktest.uni-osnabrueck.de
```
