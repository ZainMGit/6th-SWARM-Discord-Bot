# 6th SWARM Discord Bot

Bot for the 6th-SWARM Discord server.

**Commands**

`!onboard @member [optional nickname]`

- Adds 3 roles to the user
- Removes 1 role from the user
- Sets nickname to `[Pvt] <name>` or `[Pvt] <nickname>` if provided
- Requires the role defined by `ROLE_ONBOARD_ALLOWED`

**Environment Variables (.env)**
```
DISCORD_TOKEN=
GUILD_ID=
ROLE_ADD_1=
ROLE_ADD_2=
ROLE_ADD_3=
ROLE_REMOVE=
ROLE_ONBOARD_ALLOWED=
```

