[app]

# App name
title = Snake Game

# App package name
package.name = snakegame
package.domain = org.yourdomain

# App source code directory
source.dir = .
source.include_exts = py,png,jpg,wav,mp3,ttf,ico

# App requirements
requirements = python3,pygame,numpy

# App orientation
orientation = landscape

# Android specific
android.permissions = VIBRATE
android.api = 31
android.minapi = 21
android.ndk = 25b
android.skip_update = True

# App version info
version = 1.0
android.numeric_version = 10

# App icon
icon.filename = assets/images/snake_logo.png

# Extra app files
# source.include_patterns = assets/*,src/*
source.include_patterns = assets/*, src/*

[buildozer]
log_level = 2
warn_on_root = 1 