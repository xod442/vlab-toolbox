# Zero.....my hero
Very simple flask application that assists in rapidly resetting the vLab configurations.


Installation:

# must have git installed

[Install Git](https://github.com/git-guides/install-git)


# Must have docker and docker compose installed.
[Install Docker Desktop](https://www.docker.com/products/docker-desktop)

Works well with docker-desktop for macbook

```
Go to you place where you save you git projects, I use /home/user/opt.
Not to be confused with /opt, they are two different thing :-)

% git clone https://github.com/xod442/zero.git
% cd zero
zero%  docker-compose up -d
```
# Gotcha's
Running behind a proxy. You need to add all of the networks that are internal to the no_proxy
in the Dockerfile. Currently it is configured for my labs networks.
Make changes to the Dockerfile before running the docker-compose up.

#Application Notes
This application uses three main sub modules. The first one will be the
cx_zero.py file located in the utility directory. It will ROLLBACK all of the Switches
to the initial configuration file. It restores the checkpoint to the startup-config.

Next, the switches need rebooted. That is a function of afc_switchboot.py. At
this point, the running config of the switches are unchanged and the AFC is
still in communication with the switches. Leverage the AFC reboot API to reboot all switches.

When the switches boot they will return to ZERO status (Init config).

Finally vm_zero.py will kick off and it will revert every student VM back to the INITIAL state.
It will also look for any distributed virtual switches and remove them.

At this point the entire lab has been rolled back to the initial state.

[Here is some very good documentation on what to do]:
(https://www.techworldwookie.com/zero).
