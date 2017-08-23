# Discordion
*A bot for discord*

## Requirements

For base bot:

* discord.py[voice] v0.16.7
* peewee v2.9.2
* PyYAML v3.12

For Soundboard and Cat:

* requests v2.13.0

For Twitter:

* tweepy v3.5.0

For Misc:

* lenny v0.1.1

## Configuration

This bot uses a file called `config.yml` for it's configuration. An example config:

```yml
discord:
  token: <discord token>
  client_id: <discord client id>
  client_secret: <discord client_secret>
  owner: <discord owner id>
twitter:
  consumer_key: <twitter consumer key>
  consumer_secret: <twitter consumer secret>
  access_token_key: <twitter access token key>
  access_token_secret: <twitter access token secret>
extensions:
  - cogs.soundboard
  - cogs.admin
  - cogs.linker
  - cogs.rng
  - cogs.cat
  - cogs.twitter
  - cogs.misc
  - cogs.xkcd
  - cogs.economy
  - cogs.casino # Depends on cogs.economy
```

## Cogs

Key:

|Symbol|Meaning|
|---|---|
|`<>`|Argument is required.|
|`[]`|Argument is optional.|
|`x=50`|`x` defaults to 50.|
|`arg1 arg2 args...`|`args` is variable length. Can be one argument, or two, etc.|
|`[arg1 [arg2]]`|`arg1` cannot be specified without also specifying `arg2`.|

### Soundboard

Allows users to interact with a soundboard. Sounds are per-server only, except for a few, global sounds.

|Command + Arguments|Aliases|Description|Notes|
|---|---|---|---|
|`!soundboard [name] [volume]`|`sb`|Play `[name]` at `[volume]`. If both are not specified, list all sounds instead.|-|
|`!soundboard add <name> [link] [volume=50]`|`sb a`|Add a sound to the soundboard.<br>`name` - name of the sound<br>`link` - A link to the source sound file. If not specified, command must be put in the comment of a file upload.<br>`volume` - The default volume to play this sound.|-|
|`!soundboard delete <name>`|`sb d`, `sb del`, `sb remove`, `sb r`, `sb rm`|Remove sound named `<name>` from the soundboard.|-|
|`!soundboard all <name>`|-|Play a sound from the soundboard of all sounds on all servers.|Requires user to be bot owner.|
|`!soundboard globalize <name>`|-|Makes `name` a global sound (accessible to all servers).|Requires user to be bot owner.|

### Admin

Provides a few management tools for the bot owner.

|Command + Arguments|Aliases|Description|Notes|
|---|---|---|---|
|`!username <username>`|-|Changes the bot's global username.|Requires user to be bot owner.<br>Can be run twice per hour.|
|`!avatar <url>`|-|Changes the bot's avatar to the link provided.|Requires user to be bot owner.|
|`!presence <presence>`|-|Change the bot's "playing" status.|Requires user to be bot owner.|
|`!cogs`|-|List currently loaded cogs.|Requires user to be bot owner.|
|`!load <module>`|-|Load a cog.|Requires user to be bot owner.|
|`!unload <module>`|-|Unload a cog.|Requires user to be bot owner.|
|`!reload <module>`|-|Reload a cog.|Requires user to be bot owner.|
|`!debug <code>`|-|Evaluate python code. Environment includes `bot`, `ctx`, `message`, `server`, `channel`, and `author`.|Requires user to be bot owner.|

### Linker

Allows users to store text in a database to be retrieved later.

|Command + Arguments|Aliases|Description|Notes|
|---|---|---|---|
|`!link [name]`|`links`, `l`, `tag`, `tags`, `t`|Retrieve link named `link`. If not specified, will list all links|-|
|`!link add <name> <text>`|`link a`|Add a link with name `name`, linked to `text`.|-|
|`!link delete <name>`|`link d`, `link del`,`link remove`,`link r`, `link rm`|Remove the link named `name`.|-|
|`!link all <command>`|-|Retrieve a link from all links on all servers.|Requires user to be bot owner.|
|`!link globalize <name>`|-|Makes `name` a global link (accessible to all servers).|Requires user to be bot owner.|

### RNG

Generates random numbers.

|Command + Arguments|Aliases|Description|Notes|
|---|---|---|---|
|`!roll [lower=1 [upper=6]]`|`dice`, `random`, `rng`, `rand`|Generate a random number between `lower` and `upper`.|-|
|`!choose <choice1> <choice2> [other choices...]`|`decide`|Choose from two or more choices.|-|
|`!flip`|-|Flip a coin.|-|
|`!shuffle <item1> <item2> [other items...]`|-|Shuffle a list of items|-|

### Cat

Get a random cat.

|Command + Arguments|Aliases|Description|Notes|
|---|---|---|---|
|`!cat`|-|Get a random cat.|-|

### Twitter

todo

### Misc

todo

### xkcd

todo

### Economy

todo

### Casino

todo

### TL;DR

todo

## TODO

* **Handle global links/sounds with the same name.**
* Move Twitter cog to rely on webhooks instead of push updates in another thread.
* requirements.txt
* Locally generate tl;dr instead of relying on smmry
* Per user linker?
* Documentation, in general.
* Wiki maybe?
* Move dependency on requests to aiohttp.
  * Make generalized aiohttp requests module?
* Auto-generate example config.
  * Prompt for values?
* plug.dj echoing?
* playback speed control on soundboard
