These are the steps I've taken to install software on CachyOS with
intention to play SteamVR games on it. 

My hardware:
- AMD 7900XT GPU
- Intel CPU
- Quest Pro headset

And I have secure boot enabled because of windows 11. bleh.

During USB installation of CachyOS, I chose the systemd-boot bootloader, 
the ext4 filesystem for my root partition, and the niri+noctalia display manager.

# Generic package installs
 
```bash
sudo pacman -Syu geany yay #install the geany text editor and the yay package manager

yay floorp #web browser
yay htop #htop system monitor tool
yay viewnior #image viewer
```

To search packages: `yay -Ss {package name}`

To install packages: `yay {package name}`

To view package contents: `yay -Fl {package name}`

To find packages that contain the specified file: `yay -Fy {file name}`

To remove packages: `yay -Rc {package name}`

# Multidisplay setup (Noctalia / Niri)
Run the following to see your currently connected display configuration:

`niri msg outputs`

Open this file in geany to edit it: `~/.config/niri/cfg/display.kdl`
and manually enter your display configuration

The output file that works for me:
```
// ────────────── Output Configuration ──────────────
// You can run `niri msg outputs` to get the correct name for your displays.
// You will have to remove "/-" and edit it before it takes effect.
// https://github.com/YaLTeR/niri/wiki/Configuration:-Outputs

// note that the logical size of 4k monitors is 1440p (2560x1440)
//  as seen in `niri msg outputs`
// my monitor layout is the 1080p wide one on the left, and 4k
//  on the right. Their bottoms are lined up. 
// the below coordinate system is positive x = right, positive y = down
// origin is upper left
// to get the bottoms of the monitors to line up, 
//  smaller y = (bigger height - smaller height) = 1440 - 1080 = 360
output "LG Electronics LG HDR WFHD 0x0004D9E3" {
	mode "2560x1080@59.978"
	scale 1
	position x=0 y=360
}
output "LG Electronics LG HDR WFHD 0x0004D9E3" {
	mode "3840x2160@59.997"
	scale 1.5
	position x=2560 y=0
}
```

# LACT (for AMD GPUs)
When running VR games, AMD GPUs may drop some frames due to the GPU
entering a power save mode. The LACT overclocking tool can be used to
fix this.

I followed this guide to install it and set it up:
https://github.com/chaosmaou/wivrn-guide?tab=readme-ov-file#lact 

```bash
yay lact

sudo systemctl enable lactd
sudo systemctl restart lactd

lact #start LACT's UI
```

- In the OC tab, enable AMD overclocking (takes a minute or so)
- Under Performance, set the "Performance Level" to "Manual". Set the "Power Profile Mode" to "VR"
- Hit apply at the bottom of the window

Now, at some point, reboot in order for the overclocking to actually
take effect

# Steam
Install the CachyOS Steam package:

`yay steam`

Install protonGE and also protonGE-RTSP:

```bash
yay asdf-vm

#vanilla protonge
asdf plugin add protonge
asdf install protonge latest

#protonge RTSP
asdf plugin add protonge-rtsp https://github.com/founta/asdf-protonge-rtsp.git
asdf install protonge-rtsp latest
```

## VRChat
In steam, I install:
- VRChat
- ~~XSOverlay~~
- ~~OVR advanced settings~~
  - XSOverlay and OVR advanced settings do not appear to be functional
    in Linux :)

1. Right click on VRChat -> Properties -> Compatibility
2. Check "Force the use of a certain compatibility tool" and select GE proton RTSP

### VRC Video Cacher setup
The Steam version of VRC Video Cacher was non-functional for me.

```bash
#make a directory for local binaries
mkdir $HOME/.bin/

#add it to the path, so you can run them without providing the
# directory name
echo 'set -gx PATH $PATH $HOME/.bin/' > ~/.config/fish/conf.d/dotbin.fish

#and open a new terminal
```

You may need to start up VRC at least once before running the app to 
have it store your youtube cookies from their firefox plugin.

To install:
```bash
#Install a JavaScript runtime that yt-dlp wants:
yay deno

#download the latest VRCVideoCacher
cd ~/.bin/
wget https://github.com/EllyVR/VRCVideoCacher/releases/latest/download/VRCVideoCacher

chmod a+x ./VRCVideoCacher #mark VRCVideoCacher as executable

#start it like so:
VRCVideoCacher
```

Follow in-app steps to extract youtube cookies

#### Allow cached videos to play in VRC (non functional)
In the settings, set the web server URL to: `http://localhost.youtube.com:9696`

Add an alias to localhost (they will be served from "localhost.youtube.com" 
instead of "localhost.com" and VRC should be happier with that):
```
echo "127.0.0.1 localhost.youtube.com" | sudo tee -a /etc/hosts
```

This didn't seem to work. VRC Video Cacher seems to have served the cached video, but 
VRChat rejects it for whatever reason.

I've just disabled video caching for now.

## SteamVR

### Installation and setup
Install SteamVR through steam

Right click, properties and select the "beta" version under "Game versions and betas"

In the Steam settings under Interface, select the beta version of the client and restart

Set the following as the SteamVR launch options:
```
QT_QPA_PLATFORM=xcb ~/.local/share/Steam/steamapps/common/SteamVR/bin/vrmonitor.sh %command%
```

You might not need `QT_QPA_PLATFORM=xcb` if you're not on a tiling window manager. 
Not really sure when it's needed, but it was for me :)

Start SteamVR and enter superuser password if prompted to let it finish its install

### Debugging

#### SteamVR doesn't launch
The SteamVR logs are sort of messy.

The log file `~/.local/share/Steam/logs/vrclient_steam.txt` may contain useful info.

You will see errors that it cannot find `linux32` versions of the vrclient library, 
but that is totally normal -- it looks like it attempts to load the 32-bit version and then, on failure, falls back to the 
64-bit one.

My first major issue was that SteamVR didn't launch at all -- it would start up and then immediately crash. The above log file did not contain
any output at all from the times of the crashes, either :<

I didn't realize at the time that SteamVR is an X application. I am using Wayland, so the Xwayland package 
(that runs X applications under Wayland) is required. In addition to that, I also needed to add the `QT_QPA_PLATFORM=xcb`
environment variable to the SteamVR app launch options. To figure that out, I first attempted to run the `vrmonitor.sh` utility,
the one that you also place in your launch options:

```bash
cd ~/.local/share/Steam/steamapps/common/SteamVR/bin
LD_LIBRARY_PATH=$PWD/linux64 ./vrmonitor.sh
```

After running that, the following error was seen right before the application crash:
```
This application failed to start because it could not find or load the Qt platform plugin "wayland".

Available platform plugins are: xcb.
```

When googling that error, the following Reddit post (and Google's chatbot) 
led me to the solution: https://www.reddit.com/r/archlinux/comments/1910hru/qt_apps_crash_on_launch_qtqpaplugin_could_not/

### Notes

SteamVR on Linux seems to have high performance, but is buggy. I was seeing performance similar to what I was seeing on windows.
I went into an Udon Saber world in VR Chat, and it played just about as smoothly as it does in Windows!

Just a few caveats:
- When using Steam Link, there are audio issues, at least on my hardware.
  - it creates a device, but it is non-functional. Run: `systemctl --user restart pipewire pipewire-pulse wireplumber` to fix things after this happens
  - see https://github.com/ValveSoftware/SteamVR-for-Linux/issues/873
- if you accidentally click on "Desktop" in the steamvr menu (usually showing you your desktop), steam will segfault
  - after steam crashes, run: `rm -rf /tmp/steam*` before restarting (otherwise it doesn't start) 

## SteamVR streaming apps

### ALVR
ALVR is an open source replacement for eg Air Link, Virtual Desktop, Steam Link.

I followed these steps for installation: https://github.com/alvr-org/ALVR/blob/master/wiki/Installation-guide.md

#### Installation
Install Rust compilation tools:
```bash
#the following command is from: https://rust-lang.org/learn/get-started/
# select the standard installation option
yay rustup
rustup default stable
rustup install
source ~/.config/fish/conf.d/rustup.fish
```

Install ALVR:
```bash
export CARGO_BUILD_JOBS=8
yay alvr
```

Start ALVR with: `alvr_dashboard`

Follow in-app settings to install. After installation, go to the Installation page
and press "Register ALVR Driver"

Install the ALVR app from the meta store on your headset

#### Settings
ALVR has a massive number of settings. The following worked OK for me
(with the rest of the settings at default):

```
# Presets
Preferred framerate 90Hz
Codec preset H264
Eye and face tracking VRCFaceTracking

# Video
Bitrate constant 150Mbps
Image corruption fix on
Foveated encoding on
10-bit encoding: on

# Headset
Controller emulation mode = Quest Pro
Emulation mode = Quest Pro
Face tracking on
```

### Steam Link
> [!CAUTION]
> Steam Link has non-functional audio as of March 14 2026
>
> It works for some, but they need to manually connect inputs/outputs
> to the Steam Link audio devices. Try using the `helvum` or
> `qpwgraph` utilities to manually configure the Steam Link audio nodes.
> See https://github.com/ValveSoftware/SteamVR-for-Linux/issues/873 and
> https://github.com/ValveSoftware/SteamVR-for-Linux/issues/861

Folks say that recent (this was written Mar 09 2026) beta versions of Steam Link run on Linux. And it does!

To get it running:
- Install the Steam Link app on your headset (eg from the Meta store).
- Add firewall rules for Steam Link traffic (see below)
- Launch SteamVR in steam and then attempt to connect with Steam Link on the headset
  - no auto-SteamVR-launching type things that happen on Windows

Firewall rules:
```bash
sudo ufw allow 10400/udp
sudo ufw allow 10401/udp
sudo ufw allow 27031/udp
sudo ufw allow 27036/udp
sudo ufw allow 27036/tcp
sudo ufw allow 27037/tcp
```

#### Hopeless audio debugging notes
CachyOS with the Noctalia+Niri desktop environment use the `pipewire` audio utility. 
SteamVR uses ALSA and PulseAudio for audio, though. To help with that, there is the `pipewire-pulse` utility
that translates PulseAudio to pipewire.

I happened to have started steam on the command line running:
```bash
steam
```

After connecting my headset with SteamVR Link and starting VRChat, I saw the following message in the
terminal window that started steam:
```
ALSA lib pulse.c:242:(pulse_connect) PulseAudio: Unable to connect: Timeout
```

pipewire runs (at least on CachyOS) as a user systemd service. To watch  `pipewire-pulse` logs, the following can be run:
```bash
journalctl --user -f -u pipewire-pulse
```

However, this doesn't really contain any useful information. To increase logging verbosity, you can edit the `/usr/lib/systemd/user/pipewire-pulse.service` file (with `sudo` and your favorite text editor).
In this file, you can change the line starting in `ExecStart` to, for example:

```
ExecStart=/usr/bin/pipewire-pulse -vvv
```
To increase pipewire-pulse verbosity. After adding that to the service file, you can run the following commands for the service file change to take effect:

```bash
sudo systemctl daemon-reload
systemctl --user restart pipewire-pulse
```

After restarting SteamVR and restarting pipewire, watching the pipewire-pulse logs while VRChat was running showed the following error:

```
D pw.core [core.c:64:core_event_error]: 0x55b80f5cbb60: proxy 0x55b80f6f3650 id:54: bound:88 seq:406 res:-2 (No such file or directory) msg:"enum params id:16 (Spa:Enum:ParamId:ProcessLatency) failed"
```

These are benign, as it turns out.

The more telling issue was that my Desktop's (Noctalia's) audio tool became non-functional after that. When attempting to run any pipewire commands, such as `pw-dump`, which dumps the current pipewire state to json, hang indefinitely. 

When SteamVR Link starts, it seems that pipewire just entirely stops working. I can see in the system audio setting that a `Meta Quest Pro (Steam Link)` audio device was added, but selecting it does not do anything.

This sort of indicates that the last pipewire thing that happened was the creation of that virtual audio device. 

Restarting pipewire restores audio functionality, but Steam Link is non-functional audio-wise, still
```
systemctl --user restart pipewire pipewire-pulse wireplumber
```

I eventually wrote the following script to attempt to print the state of pipewire before things break. Here's the script:
```python3
import subprocess, time

try:
    vrserver_outputs = []
    cmd = ["pw-dump", "--no-colors"]
    while True:
        pw_dump = subprocess.check_output(cmd).decode("utf-8")
        if "Meta Quest Pro" in pw_dump:
            vrserver_outputs.append(pw_dump)
        time.sleep(0.01)
except subprocess.CalledProcessError:
    pass
except KeyboardInterrupt:
    pass

print("num vrserver info: %d" % (len(vrserver_outputs)))
if len(vrserver_outputs):
    with open("vrserver_pw_info.txt", "w") as f:
        for out in vrserver_outputs:
            f.write(out)
            f.write("\n")
```

This runs `pw-dump` over and over and looks for SteamVR's audio device. I somehow got lucky and was able to catch the SteamVR audio device before things broke. This is part of the audio sink (eg speakers) node it created:
```
  {
    "id": 80,
    "type": "PipeWire:Interface:Node",
    "version": 3,
    "permissions": [ "r", "w", "x", "m" ],
    "info": {
      "max-input-ports": 129,
      "max-output-ports": 0,
      "change-mask": [ "input-ports", "output-ports", "state", "props", "params" ],
      "n-input-ports": 0,
      "n-output-ports": 0,
      "state": "suspended",
      "error": null,
      "props": {
        "adapt.follower.spa-node": "",
        "audio.channels": 2,
        "audio.rate": 48000,
        "client.id": 76,
        "clock.quantum-limit": 8192,
        "device.icon-name": "network-wireless",
        "factory.id": 9,
        "library.name": "audioconvert/libspa-audioconvert",
        "media.category": "Playback",
        "media.class": "Audio/Sink",
        "media.name": "vrlink_output",
        "media.role": "Game",
        "media.software": "Steam Link",
        "media.type": "Audio",
        "node.autoconnect": true,
        "node.description": "🥽 Meta Quest Pro (Steam Link)",
        "node.loop.name": "data-loop.0",
        "node.name": "vrserver",
        "node.want-driver": true,
        "object.id": 80,
        "object.register": false,
        "object.serial": 523,
        "port.group": "stream.0",
        "steamvr.internal": true,
        "stream.is-live": true
...
```

There are no input or output ports! What the frick kind of audio thing is this?

I didn't see anything obvious to indicate that SteamVR was 
causing a pipewire issue in its logs (other than timeouts), and I 
didn't see anything obviously wrong happening in the pipewire logs 
(other than this "vrserver" node being suspended immediately after 
creation, presumably due to it not having any inputs or outputs).

Looking at the logs others posted to GitHub, a couple users
were able to get SteamVR Link audio working on CachyOS using the KDE 
Plasma desktop environment (or at least the SteamVR Link pipewire stuff
was able to set up the vrserver node; I saw some evidence of it connecting
nodes like so in the 
[steam-logs.tar.gz](https://github.com/user-attachments/files/24936684/steam-logs.tar.gz) 
posted [here](https://github.com/ValveSoftware/SteamVR-for-Linux/issues/861)):
```
Thu Jan 29 2026 23:43:28.323135 [Info] - [CVRPipewireAppManager] Creating link from OUT(MAX:0/2) 118:176 (0x7f283800a130) to IN(MAX:2/2) 154:159 (0x7f283800aef0) (class: 1)
Thu Jan 29 2026 23:43:28.323149 [Info] - [CVRPipewireAppManager] Creating link from OUT(MAX:0/2) 118:190 (0x7f283800a260) to IN(MAX:2/2) 154:187 (0x7f283800b150) (class: 1)
```

Maybe don't use the beta version of SteamVR?
- same issue

If you use the `pipewire-media-session` pipewire session manager instead
of `wireplumber`, pipewire at least doesn't hang indefinitely when Steam
Link makes its nodes. Note that this session manager is deprecated at the
time of writing (Mar 14 2026).

```bash
yay pipewire-media-session
```

Anywho, I give up debugging. WiVRn audio works fine and Steam Link is able
to interface with pipewire (to make those initial devices), so this is 
probably a Steam Link bug.

I later tested that this bug is also present on my machine when running a fresh Cachy install
with the KDE desktop, and on a fresh EndeavourOS install with the GNOME desktop.

This script for later reference: 
https://github.com/l33tlinuxh4x0r/alvr-audio-script/blob/main/avlr-audio.sh

You can set the audio driver for VRChat to ALSA instead of pulse if you 
want, but there isn't a point, doesn't help

```bash
yay protontricks
yay pipewire-alsa
protontricks 438100 sound=alsa
```

Get the steam ID for a game by going to the store page and copying the
number from the URL

#### Goofy solution (don't do this)
One thing I used for a single night (and it was not great) was an audio stream
I ran from a server on my PC and accessed through the Quest's web browser ...

It sounds like a bad idea and it was :)

Dependencies:
```bash
yay mediamtx-bin #media server

#write mediamtx configuration
echo "paths:
  vr: 
    source: {}
" > ~/.config/mediamtx/mediamtx.yml

#start and enable the media server
sudo systemctl enable mediamtx
sudo systemctl start mediamtx

#the default WebRTC port for mediaMTX is 8889
sudo ufw allow 8889/tcp

#we're going to make an audio processing pipeline using GStreamer, so install
# some GStreamer components
yay gst-devtools
yay gst-plugin-pipewire
yay gst-plugins-good
yay gst-plugins-bad
yay gst-plugins-ugly

export CARGO_BUILD_JOBS=8
yay gst-plugins-rs-git #this takes forever to compile

#I set the number of build jobs lower because the compilation by default
# uses all CPU cores. For whatever reason rustc was segfaulting when that
# was going on
```

Now you can use this python script to start an audio stream on
`http://{your desktop's IP address}:8889/vr`. You can connect to it from
any device on your LAN from their web browser (eg your headset!).

The script creates a virtual audio sink and sets it as the default playback
device, and makes a GST pipeline to push the audio to the media server.

See the "start_vr_audio.py" python script in this repository.

## WiVRn (SteamVR replacement for wireless headsets)
WiVRn is an all-in-one replacement for SteamVR and whatever streaming
app used for streaming video from your headset.

I followed this tutorial: https://lvra-gitlab-io-802e4a.gitlab.io/docs/fossvr/wivrn/

WiVRn github: https://github.com/WiVRn/WiVRn

Comprehensive guide: https://github.com/chaosmaou/wivrn-guide

### Installation
Install AUR wivrn and also xrizer:

```bash
yay wivrn-dashboard

#install xrizer -- OpenVR runtime without SteamVR
yay xrizer
```

WiVRn does system discovery using the following service, need to enable it:

```bash
sudo systemctl enable avahi-daemon
sudo systemctl start avahi-daemon
```

WiVRn and avahi use these ports, open them up in the firewall:

```bash
sudo ufw allow 5353/udp
sudo ufw allow 9757/tcp
sudo ufw allow 9757/udp
```

- Start the WiVRn dashboard on your PC and start going through the setup steps
- Install the WiVRn app through the Meta store
- Follow steps in the dashboard to finish setup

Make sure to update all previously installed SteamVR apps with the following 
launch option as suggested by the wivrn dashboard:

```bash
PRESSURE_VESSEL_IMPORT_OPENXR_1_RUNTIMES=1 %command%
```

# Tracking setup
## SlimeVR
The LVRA wiki has very good steps on SlimeVR installation: https://wiki.vronlinux.org/docs/slimevr/

The SlimeVR AppImage here does not work for me: https://github.com/SlimeVR/SlimeVR-Server/releases/latest/download/SlimeVR-amd64.appimage

Install the latest binaries:
```bash
yay slimevr-beta-bin
```

Install the SteamVR driver:
```bash
cd ~/Downloads
wget https://github.com/SlimeVR/SlimeVR-OpenVR-Driver/releases/latest/download/slimevr-openvr-driver-x64-linux.zip

cd ~/.steam/steam/steamapps/common/SteamVR/drivers && unzip ~/Downloads/slimevr-openvr-driver*
```

Install the feeder app
```bash
cd ~/Downloads

wget https://github.com/SlimeVR/SlimeVR-Feeder-App/releases/latest/download/SlimeVR-Feeder-App-Linux.zip
cd ~/.bin/ && unzip ~/Downloads/SlimeVR-Feeder*

#patch feeder app manifest for linux
cd ~/.bin/SlimeVR-Feeder* &&  sed -i '7i\ \t\t"binary_path_linux": "SlimeVR-Feeder-App",' ./manifest.vrmanifest

#register it with SteamVR
mkdir -p ~/bkup && cp ~/.steam/steam/config/appconfig.json ~/bkup/
python3 -c "
import json
app_conf_fname = '$HOME/.steam/steam/config/appconfig.json'
with open(app_conf_fname, 'r') as f:
  app_config = json.load(f)
app_config['manifest_paths'].append('$HOME/.bin/SlimeVR-Feeder-App-Linux/manifest.vrmanifest')
with open(app_conf_fname, 'w') as f:
  json.dump(app_config, f, indent=2)
"
```

Now start SteamVR, and in the settings menu under "Startup / Shutdown", 
enable the slimeVR feeder app as a startup overlay app.

## Face tracking
The LRVA group has a list of VRChat facetracking softwares: https://lvra.gitlab.io/docs/vrchat/facetracking/

### VRCFT Avalonia
Cross-platform implementation of the windows VRC Face Tracking app.
https://github.com/dfgHiatus/VRCFaceTracking.Avalonia

v1.1.1.0 seems to be bugged: https://github.com/dfgHiatus/VRCFaceTracking.Avalonia/issues/47

Also, make sure to start VRCFT Avalonia before starting VR Chat

Install (v1.0.0.0 appimage):
```bash
#prereqs
yay fuse2

#assumes ~/.bin exists
cd ~/.bin/
wget https://github.com/dfgHiatus/VRCFaceTracking.Avalonia/releases/download/v1.0.0.0/VRCFaceTracking.Avalonia.Desktop.x64.AppImage

#set the app image as executable
chmod a+x ./VRCFaceTracking.Avalonia*
```

Add modules for your eye/face tracking solution

Set autostart to on in the settings

# WayVR
https://github.com/wayvr-org/wayvr

Overlay and playspace adjuster

## Install and launching
Install (AUR):
```bash
yay wayvr-git
```

WayVR needs to be launched after linking up your headset with eg Steam Link, ALVR, etc. 
It defaults to autostarting after you launch it for the first time.

When using Steam Link with audio issues (as of 3-22 on Arch-based distributions), disable WayVR autostart
and manually start it up after restarting pipewire after Steam Link breaks it.

Edit the controller bindings to bring up the WayVR overlay and playspace dragging features
with Steam VR's bindings UI.

## Input configuration
When starting WayVR, an error will be emitted indicating issues with the mouse and keyboard, with instruction to resolve:

Enable the uinput kernel module and add ourselves to the input group:
```bash
sudo usermod -a -G input $(whoami)
echo "uinput" | sudo tee /etc/modules-load.d/uinput.conf
```

And reboot

## Watch overlay timezone change
Note: list available timezones by running `timedatectl list-timezones`

```bash
echo '
timezones:
- "Japan"
- "Greenwich"
' > ~/.config/wayvr/conf.d/clock.yaml
```

## Misc configuration

Set "Handsfree mode" to None to remove the ~10s delay before being able
to interact with WayVR's menus via controller.

## Building from source
ref: https://github.com/wayvr-org/wayvr/wiki/Building-from-Source

Install dependencies as listed in the above document

```bash
cd ~/src
git clone --recursive -b main git@github.com:wayvr-org/wayvr.git
cd wayvr

#make edits

cargo build --release --no-default-features --features=wayland,openvr

RUST_LOG=debug ./target/release/wayvr
```

#### SteamVR
In the SteamVR settings after connecting your headset, enable OSC and sending of eye and face tracking info.
Select 9015(ALT) as the output port.

# SteamVR start script
Starts slimevr, VRC Video Cacher, VRCFT Avalonia, and SteamVR. Also 
restarts pipewire after Steam Link connects.
```bash
echo '#!/bin/fish

#on keyboard interrupt, stop all subprocesses
function kill_jobs
  #send interrupt to all jobs
  jobs -p | tail -n+1 | xargs kill -2
  sleep 5
  jobs -p | tail -n+1 | xargs kill -9
end
trap kill_jobs SIGINT

slimevr &
VRCVideoCacher &
VRCFaceTracking.Avalonia.Desktop.x64.AppImage &

sleep 0.5

#start SteamVR
steam steam://rungameid/250820 &

#wait until steam link is started, then restart pipewire to use other audio 
# (because Steam Link\'s audio is broken right now)
#also start WayVR afterwards
while [ 1 ]
  if [ "$(pgrep vrcompositor | wc -l)" -ne "0" ]
    sleep 3
    systemctl --user restart pipewire pipewire.socket wireplumber.service pipewire-pulse.service pipewire-pulse.socket
    wayvr &
    break
  else
    sleep 0.5
  end
end
sleep infinity
' > ~/.bin/vr_start.fish
chmod a+x ~/.bin/vr_start.fish
```

# VRChat avatar creation software

Reference: https://wiki.vronlinux.org/docs/vrchat/unity/

Package installs:
```bash
yay blender #extra repo
yay unityhub #AUR
```

## ALCOM
Open source VRC Creator Companion

### Install from AUR
```bash
yay alcom-bin #AUR
```

### AppImage (doesn't seem to work, white screen issue as mentioned in the VRLA wiki)
Download appimage from: https://vrc-get.anatawa12.com/en/alcom/

```bash
#assumes ~/.bin exists and is added to the path, and that the AppImage is in Downloads
cd ~/.bin/
mv ~/Downloads/alcom*.AppImage ./

#set the app image as executable
chmod a+x ./alcom*.AppImage
```

## Unity setup

Under Edit->Project Settings, go to the Player section. Uncheck the 
"Auto Graphics API for Linux" box. Re-arrange the options such that the
Vulkan API is first in the list.

Otherwise, liltoon shaders will not render properly in the editor:
https://github.com/lilxyzw/lilToon/issues/329

You seem to have to do this every time you open your project :<

# Miscellaneous packages

```bash
yay kicad
yay code #visual studio code

yay discord
```

# Add Windows boot entry to bootloader
For my system that has Windows installed on another drive

## systemd-boot
Reference: https://wiki.archlinux.org/title/Systemd-boot

```bash
yay edk2-shell
sudo mkdir /boot/EFI/tools/
sudo cp /usr/share/edk2-shell/x64/Shell.efi /boot/EFI/tools/shellx64.efi
echo '
title    UEFI shell
efi      /EFI/tools/shellx64.efi
sort-key e
' | sudo tee /boot/loader/entries/edk2-shell.conf

#now follow the steps here to determine the filesystem alias for the drive containing the Windows EFI partition
# wiki.archlinux.org/title/Systemd-boot#Boot_from_another_disk
#in my case, it is HD2b
echo '
title    Windows
efi      /EFI/tools/shellx64.efi
options  -nointerrupt -nomap -noversion HD2b:EFI\Microsoft\Boot\bootmgfw.efi
sort-key w
' | sudo tee /boot/loader/entries/windows.conf

#and reboot to see if things worked:
sudo reboot now

#they do!
```

## rEFInd bootloader setup (nonfunctional)
I did not get this to work -- refind does not launch after MOK enrollment

https://wiki.archlinux.org/title/REFInd

https://www.rodsbooks.com/refind/secureboot.html

```bash
yay refind
yay shim-signed #
yay mokutil #cachyos-extra-v3
sudo refind-install --shim /usr/share/shim-signed/shimx64.efi
sudo mokutil -i /usr/share/refind/keys/refind.cer
sudo reboot now #you will have to do MOK enrollment and hopefully refind can launch after
```
