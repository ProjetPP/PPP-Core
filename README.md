# PPP Core application.

[![Build Status](https://scrutinizer-ci.com/g/ProjetPP/PPP-Core/badges/build.png?b=master)](https://scrutinizer-ci.com/g/ProjetPP/PPP-Core/build-status/master)
[![Code Coverage](https://scrutinizer-ci.com/g/ProjetPP/PPP-Core/badges/coverage.png?b=master)](https://scrutinizer-ci.com/g/ProjetPP/PPP-Core/?branch=master)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/ProjetPP/PPP-Core/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/ProjetPP/PPP-Core/?branch=master)


# How to install

With a recent version of pip:

```
pip3 install git+https://github.com/ProjetPP/PPP-Core.git
```

With an older one:

```
git clone https://github.com/ProjetPP/PPP-Core.git
cd PPP-Core
python3 setup.py install
```

Use the `--user` option if you want to install it only for the current user.

# How to run the router (for system administrators)

You can write your `config.json` file in a quite straightforward way, using
the file `example_config.json` as an example.

Then, just run:

```
PPP_CORE_CONFIG=/path/to/json/config.json gunicorn ppp_core:app
```
