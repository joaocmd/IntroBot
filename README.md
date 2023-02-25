# vxTwitterBot

A Discord bot that plays an intro song when a users joins a voice channel.

## Bot Usage

Commands:
* `set`: sets intro to file specified in `url`. Supports links to download media files and youtube links;
* `setttachment`: sets intro to file given as an attachment;
* `setother`: sets intro of `other` to file specified in `url`. Supports links to download media files and youtube links. Only available for users with specified roles;
* `settothertachment`: sets intro of `other` to file given as an attachment. Only available for users with specified roles;
* `remove`: removes the user's intro;
* `removeother`: removes the intro of `other`. Only available for users with specified roles.

## Setup

Copy the `config-template.json` to a `config.json` and edit as necessary.
The config file is structured as follows:

```json
{
    "DISCORD_TOKEN": "<DISCORD_TOKEN_HERE>",
    "MOD_ROLES": ["DJ"]
}
```

Users with any role in `MOD_ROLES` are allowed to use the commands to set other users' intros.

### Necessary bot permissions

The scopes are necessary to run the bot:
* `bot`
* `applications.commands`

The following permissions are necessary to run the bot:
* Connect
* Speak
