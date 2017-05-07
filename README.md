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
```

## TODO
* Documentation, in general
* Move dependency on requests to aiohttp
    * Make generalized aiohttp requests module?
* Generate example config.