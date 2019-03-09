# Streaming Server

If web playback is required, a streaming server will be necessary.
https://github.com/revmischa/rtsp-server is a lightweight streaming server that
is fairly easy to set up on a raspberry pi. Here is an example using ffmpeg to
send webcam video from a macbook to the server running on a raspberry pi, and
then retrieve the video again.

install_streaming_server.sh will clone and install it for you on a raspberry pi.
Must have sudo power.

For example:

To run the server on the raspberry pi:
```
./rtsp-server/rtsp-server.pl --clientport 10000 --serverport 10001
```
Streams can be sent to port 10001 and retrieved from port 10000

To send:
```
 ffmpeg -f avfoundation -re -i "0" -f rtsp -muxdelay 0.1 rtsp://ip.of.raspberry.pi:10001/stream_name
```

And to retrieve:
```
ffmpeg -i rtsp://ip.of.raspberry.pi:10000/stream_name out.mp4
```
