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

## Usage

```
❯ proteuscmd
usage: proteuscmd [-h] [--view {all,intern,extern}] {get,set,delete} domain [target]
```

Get information about a DNS record:
```
❯ proteuscmd get lktest.uni-osnabrueck.de
```

Set an alias record:
```
❯ proteuscmd set lktest.uni-osnabrueck.de vm123.rz.uni-osnabrueck.de
```

Set a host record:
```
❯ proteuscmd set lktest.uni-osnabrueck.de 131.12.65.123
```

Delete a record:
```
❯ proteuscmd delete lktest.uni-osnabrueck.de
```
