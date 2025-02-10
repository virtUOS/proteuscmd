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

You can also specify a map of automatic replacements for domains.
This can be useful if, for example, all your domains also have an alternate domain with a `DNAME` record.
```json
{
	...
	"replace": {
		".ex.com": ".example.com"
	}
}
```

Furthermore, you can configure maps between IPv4 and IPv6 networks:
```json
{
    ...
    "v4_v6_map": [
        {
            "cidr": "192.168.22.0/23",
            "prefix": "2001:123:456:789::/64"
        }
    ]
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

## Shell Completion

The `proteuscmd` command line tool supports shell completion for several major shells:

For **Bash**, add to `~/.bashrc`:

```
eval "$(_PROTEUSCMD_COMPLETE=bash_source proteuscmd)"
```

For **ZSH**, add to `~/.zshrc`:

```
eval "$(_PROTEUSCMD_COMPLETE=zsh_source proteuscmd)"
```

For **fish**, add to `~/.config/fish/completions/proteuscmd.fish`:

```
_PROTEUSCMD_COMPLETE=fish_source proteuscmd | source
```
