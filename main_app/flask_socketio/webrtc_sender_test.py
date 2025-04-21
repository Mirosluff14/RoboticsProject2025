import asyncio
import fractions
import numpy as np
import cv2

from aiortc import MediaStreamTrack, RTCPeerConnection
from aiortc.contrib.signaling import TcpSocketSignaling
from av import VideoFrame
from picamera2 import Picamera2

class PicameraStreamTrack(MediaStreamTrack):
    kind = "video"

    def __init__(self, picam2):
        super().__init__()
        self.picam2 = picam2
        self.picam2.configure(self.picam2.create_video_configuration(main={"size": (640, 480)}))
        self.picam2.start()

    async def recv(self):
        frame = self.picam2.capture_array()
        pts, time_base = await self.next_timestamp()
        video_frame = VideoFrame.from_ndarray(frame, format="bgr24")
        video_frame.pts = pts
        video_frame.time_base = time_base
        return video_frame

async def run():
    picam2 = Picamera2()
    track = PicameraStreamTrack(picam2)

    pc = RTCPeerConnection()
    pc.addTrack(track)

    signaling = TcpSocketSignaling("receiver_ip", 9999)
    await signaling.connect()

    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)
    await signaling.send(pc.localDescription)

    answer = await signaling.receive()
    await pc.setRemoteDescription(answer)

    await asyncio.Future()  # run forever

asyncio.run(run())
