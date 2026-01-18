[app]

title = Murder Game
package.name = murdergame
package.domain = org.murdergame
source.dir = .
source.include_exts = py,png,jpg,kv,json
version = 1.0

p4a.branch = develop

requirements = python3,kivy,libffi
orientation = portrait

fullscreen = 1

android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.archs = arm64-v8a, armeabi-v7a

android.permissions = INTERNET

presplash.filename = skins/1.png
icon.filename = skins/1.png

[buildozer]

log_level = 2
warn_on_root = 0
