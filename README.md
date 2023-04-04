# Proteus Command Line Client

A simple command line client to modify DNS entries in Proteus.

## Installation

Use `pip` to install `proteus-cli`:

```
❯ pip install proteus-cli
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

## Usage

```
❯ proteus-cli
usage: proteus-cli [-h] [--view {all,intern,extern}] {get,set,delete} domain [target]
```

Get information about a DNS record:
```
❯ proteus-cli get lktest.uni-osnabrueck.de
```

Set an alias record:
```
❯ proteus-cli set lktest.uni-osnabrueck.de vm123.rz.uni-osnabrueck.de
```

Set a host record:
```
❯ proteus-cli set lktest.uni-osnabrueck.de 131.12.65.123
```

Delete a record:
```
❯ proteus-cli delete lktest.uni-osnabrueck.de
```
