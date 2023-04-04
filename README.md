# Proteus Command Line Client

A simple command line client to modify DNS entries in Proteus.

## Installation

Use `pip` to install `proteuscli`:

```
❯ pip install proteuscli
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
❯ proteuscli
usage: proteuscli [-h] [--view {all,intern,extern}] {get,set,delete} domain [target]
```

Get information about a DNS record:
```
❯ proteuscli get lktest.uni-osnabrueck.de
```

Set an alias record:
```
❯ proteuscli set lktest.uni-osnabrueck.de vm123.rz.uni-osnabrueck.de
```

Set a host record:
```
❯ proteuscli set lktest.uni-osnabrueck.de 131.12.65.123
```

Delete a record:
```
❯ proteuscli delete lktest.uni-osnabrueck.de
```
