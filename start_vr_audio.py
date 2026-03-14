import subprocess, json, argparse

#this script creates a virtual audio sink, and then creates a gst pipeline
# to stream the audio sent to it to your local network. You'll need to
# open up that port in the firewall
#on the VR headset side, open up the web browser and connect to your computer's
# IP address and port. eg 192.168.50.45:8889/vr
#this assumes you have the following configuration in ~/.config/mediamtx/mediamtx.yml:
'''
paths:
  vr:
    source: {}
'''
# and the following packages installed:
'''
gst-devtools
gst-plugin-pipewire
gst-plugins-bad
gst-plugins-good
gst-plugins-rs-git
gstreamer

mediamtx
'''
#and that you use pipewire as your audio solution


parser=argparse.ArgumentParser()
parser.add_argument("--port", type=int, help="Port to stream audio on", default=8889)
args = parser.parse_args()

port = args.port

#create sink and set as default device
module_id = None
virtual_node_cmd = "pactl load-module module-null-sink " +\
	"sink_name=vr_stream sink_properties=node.description="+\
	  "'Virtual audio device for streaming to Steam Link headset' "+\
	"format=s16le rate=48000 channels=2 && " +\
	"pactl set-default-sink vr_stream"
module_id = int(subprocess.check_output(virtual_node_cmd, 
	shell=True).decode("utf-8"))

try:
	pipewire_devices = json.loads(subprocess.check_output(["pw-dump"]).decode("utf-8"))
	vraudio_id = None
	for dev in pipewire_devices:
		if dev["type"] == "PipeWire:Interface:Node":
			if dev["info"]["props"]["node.name"] == "vr_stream":
				vraudio_id = dev["id"]

	if vraudio_id is None:
		raise RuntimeError("Unable to find created virtual audio device!")
	
	print("Virtual node id: %d" % (vraudio_id))
	
	stream_url = 'http://0.0.0.0:%d/vr/whip' % (port)
	print("Streaming to " + stream_url + " ...")
#		audioconvert ! audioresample ! \

	#now create the audio pipeline and start it
	gst_command = """gst-launch-1.0 \
		pipewiresrc path=%d ! \
		audio/x-raw,format=S16LE,rate=48000,channels=2 ! \
		queue leaky=upstream max-size-time=5000000 ! \
		opusenc bitrate=256000 bandwidth=wideband frame-size=5 ! \
		rtpopuspay ! rtprtxqueue max-size-time=5 ! \
		whipsink whip-endpoint='%s'
	""" % (vraudio_id, stream_url)
	subprocess.run(gst_command, shell=True)
except:
	if module_id is None:
		print("Unable to determine which virtual audio device is ours ... \n"
			"run pw-dump to determine the audio device ID, and unload it with \n"
			"\tpactl unload-module (id)")
		exit()
	print("Removing virtual audio device ...")
	subprocess.run(["pactl", "unload-module", str(module_id)])
