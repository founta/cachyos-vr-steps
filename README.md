I installed CachyOS from USB with systemd-boot bootloader, 
ext4 partition, and niri+noctalia display manager

# Generic package installs
 
```bash
sudo pacman -Syu geany yay #install the geany text editor and the yay package manager

yay htop #htop system monitor tool
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

An example output file that works for me:
```
// ────────────── Output Configuration ──────────────
// You can run `niri msg outputs` to get the correct name for your displays.
// You will have to remove "/-" and edit it before it takes effect.
// https://github.com/YaLTeR/niri/wiki/Configuration:-Outputs

/- output "DP-1" {
    mode "2560x1440@359.979" // Set resolution and refresh rate
    scale 1 // No scaling (use 2 for HiDPI)
}

output "LG Electronics LG HDR WFHD 0x0004D9E3" {
	mode "2560x1080@59.978"
	scale 1
	position x=0 y=0
}
output "LG Electronics LG HDR WFHD 0x0004D9E3" {
	mode "3840x2160@59.997"
	scale 1.5
	position x=2560 y=0
}
```

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
In steam, install:
- VRChat
- XSOverlay
- OVR advanced settings

Right click on VRChat -> Properties -> Compatibility
Check "Force the use of a certain compatibility tool" and select GE proton RTSP

### VRC Video Cacher setup
The Steam version of VRC Video Cacher was non-functional for me

```bash
sudo mkdir /opt/vrc_video_cacher
sudo chown $USER:$USER /opt/vrc_video_cacher
```

Install a JavaScript runtime that yt-dlp wants:
```bash
yay deno
```

```bash
cd /opt/vrc_video_cacher
wget https://github.com/EllyVR/VRCVideoCacher/releases/latest/download/VRCVideoCacher

chmod a+x ./VRCVideoCacher
```

Follow in-app steps to extract youtube cookies

## SteamVR
Folks say that recent (this was written Mar 09 2026) beta versions of Steam Link run on Linux. And it does! The performance seems very good, but it was difficult to figure out how to get running :<

### Installation and setup
Install SteamVR through steam

Right click, properties and select the "beta" version under "Game versions and betas"

In the Steam settings, select the beta version of the client

Set the following as the SteamVR launch options:
`QT_QPA_PLATFORM=xcb ~/.local/share/Steam/steamapps/common/SteamVR/bin/vrmonitor.sh %command%`

You probably don't need `QT_QPA_PLATFORM=xcb` if you're not on wayland

Start SteamVR and enter superuser password to let it finish its install

Open up ports in the firewall for it
```bash
sudo ufw allow 10400/udp
sudo ufw allow 10401/udp
sudo ufw allow 27031/udp
sudo ufw allow 27036/udp
sudo ufw allow 27036/tcp
sudo ufw allow 27037/tcp
```

Install this steam link dependency (not needed)

```bash
yay lib32-libpulse
```

#### Audio with pipewire
When steam link attempts to connect to pipewire-pulse, pipewire stops working

Replace the following packages:

```
cachyos-extra-v3/pipewire-alsa
cachyos-extra-v3/pipewire-audio
cachyos-extra-v3/wireplumber
cachyos-extra-v3/libpipewire
cachyos-extra-v3/libwireplumber
cachyos-extra-v3/pipewire
cachyos-extra-v3/gst-plugin-pipewire
```


Don't do this:
`yay -Rc pipewire-alsa pipewire-audio wireplumber libpipewire libwireplumber pipewire gst-plugin-pipewire`

```bash
yay -Rc pipewire-pulse pipewire-alsa
sudo pacman -Syu extra/gst-plugin-pipewire

yay pipewire-pulse
```

I am using this script as a the starting point:
https://github.com/l33tlinuxh4x0r/alvr-audio-script/blob/main/avlr-audio.sh



### Notes

Steam Link on Linux is actually wildly performant. I was seeing performance similar to what I was seeing on windows.
I went into an Udon Saber world in VR Chat, and it played just about as smoothly as it does in Windows!

Just a few caveats:
- it takes much longer to launch games for whatever reason
- it cannot connect to pipewire, no audio. There's something screwy going on
  - it creates a device, but it is non-functional. Run: `systemctl --user restart pipewire pipewire-pulse wireplumber` to fix things after this happens
- if you accidentally click on "Desktop" in the steamvr menu (usually showing you your desktop), steam will segfault
  - after steam crashes, run: `rm -rf /tmp/steam*`
- you seem to need to launch SteamVR in steam and then attempt to connect with steam link on the headset
  - no auto-launching type things that happen on Windows

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

#### SteamVR doesn't play audio
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

Interrogating Google's AI suggested that SteamVR is requesting a latency from pipewire that could not be handled. This could be resolved by editing the `~/.config/pipewire/pipewire-pulse.conf` file. If it does not exist, you can copy the default from `/usr/share/pipewire/pipewire-pulse.conf`

In that file, I added the following to the `pulse.rules` section:

```
{
	# If the application is Steam, don't allow it to change the global latency
	matches = [ { application.process.binary = "steam" } ]
	actions = {
		update-props = {
			pulse.min.quantum = 512/48000
			pulse.min.req          = 512/48000      # 10.6ms
			pulse.idle.timeout     = 5
		}
	}
}
```
This sets the minimum latency steam can request to 10.6ms. This is also mostly copied from one of the other rules in that configuration file.

After restarting pipewire-pulse (`systemctl --user restart pipewire-pulse`), it seemed that that error is no longer emitted from `pipewire-pulse`

However, this does not fix the audio situation. There is still no output. When SteamVR Link starts, it seems that pipewire just entirely stops working. I can see in the system audio setting that a `Meta Quest Pro (Steam Link)` audio device was added, but selecting it does not do anything.

To show the available pipewire devices, you can run: `wpctl status`. However, this just hangs forever after Steam Link starts until pipewire, pipewire-pulse and wireplumber are restarted:
```
systemctl --user restart pipewire pipewire-pulse wireplumber
```

TODO figure out why pipewire hangs when SteamVR link starts :<

## WiVRn (Steam Link replacement for Oculus quest headsets)
I followed this tutorial: https://lvra-gitlab-io-802e4a.gitlab.io/docs/fossvr/wivrn/

WiVRn github: https://github.com/WiVRn/WiVRn

Comprehensive guide: https://github.com/chaosmaou/wivrn-guide


Install package manager's wivrn and also OpenComposite:

```bash
yay wivrn-server
yay wivrn-dashboard

#install opencomposite -- OpenVR runtime without SteamVR
yay opencomposite-git
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

Start the WiVRn dashboard on your PC and start going through the setup steps
Install the WiVRn app through the Meta store
Follow steps in the dashboard to finish setup

Make sure to update all previously SteamVR apps with the following 
launch option as suggested by the wivrn dashboard:

`PRESSURE_VESSEL_IMPORT_OPENXR_1_RUNTIMES=1 %command%`

### LACT (for AMD GPUs)
```bash
yay lact

sudo systemctl enable lactd
sudo systemctl restart lactd

lact #start LACT's UI
```
In the OC tab, enable AMD overclocking

Set up LACT following this guide: https://github.com/chaosmaou/wivrn-guide?tab=readme-ov-file#lact

# Tracking setup
## SlimeVR
TODO

## Face tracking
Following: https://lvra-gitlab-io-802e4a.gitlab.io/docs/vrchat/facetracking/

TODO

# Miscellaneous packages

```bash
yay kicad
yay code #visual studio code
```

# Add Windows boot entry to systemd-boot
For my system that has Windows installed on another drive

Reference: https://wiki.archlinux.org/title/Systemd-boot

```bash
yay edk2-shell
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
