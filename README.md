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

Instead of putting in a plaintext password, you can also specify a command to run for getting the password.
This way, you can e.g. extract the password from a password manager:
```json
{
	"user": "api-user",
	"password_cmd": ["gopass", "show", "-o", "/my/proteus/pass"],
	"url": "https://proteus.example.com"
}
```

The comand can be set either as an array, or as a shell string.

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

You can configure maps between IPv4 and IPv6 networks:
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

Finally, you can configure default values for admin information.
You can still overwrite them on the command line if needed.
```json
{
    ...
    "admin_email": "someone@example.com",
    "admin_name": "John Doe",
    "admin_phone": "1234"
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

The `ip get`, `ip set`, and `ip delete` commands support a `--version` option to control which IP version to operate on. You can use `4`, `6`, or `both`. When `--version both` is specified, the command will execute for both IPv4 and IPv6 simultaneously using the v4/v6 mapping configuration:

```
# Get IP info for both IPv4 and IPv6
❯ proteuscmd ip get 192.168.1.1 --version both
{
  "v4": { "id": "...", "address": "192.168.1.1", ... },
  "v6": { "id": "...", "address": "2001:db8::1", ... }
}

# Assign an IP to both IPv4 and IPv6
❯ proteuscmd ip set 192.168.1.1 AA:BB:CC:DD:EE:FF --version both -e admin@example.com -n Admin -p 555-1234

# Delete an IP assignment for both IPv4 and IPv6
❯ proteuscmd ip delete 192.168.1.1 --version both
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
