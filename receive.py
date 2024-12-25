import pyaudio
import argparse
import asyncio
import aiohttp
import json
import os
import sys
import wave
import websockets

from datetime import datetime

startTime = datetime.now()

all_audio_data = []
all_transcripts = []
BLACKHOLE_DEVICE_INDEX = 1

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 8000

audio_queue = asyncio.Queue()

# Mimic sending a real-time stream by sending this many seconds of audio at a time.
# Used for file "streaming" only.
REALTIME_RESOLUTION = 0.25

subtitle_line_counter = 0


def subtitle_time_formatter(seconds, separator):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02}{separator}{millis:03}"


def subtitle_formatter(response, format):
    global subtitle_line_counter
    subtitle_line_counter += 1

    start = response["start"]
    end = start + response["duration"]
    transcript = response.get("channel", {}).get("alternatives", [{}])[0].get("transcript", "")

    separator = "," if format == "srt" else '.'
    prefix = "- " if format == "vtt" else ""
    subtitle_string = (
        f"{subtitle_line_counter}\n"
        f"{subtitle_time_formatter(start, separator)} --> "
        f"{subtitle_time_formatter(end, separator)}\n"
        f"{prefix}{transcript}\n\n"
    )

    return subtitle_string


# Used for BlackHole streaming only (replaces mic)
def blackhole_callback(input_data, frame_count, time_info, status_flag):
    audio_queue.put_nowait(input_data)
    return (input_data, pyaudio.paContinue)


async def run(callback, key, format, **kwargs):
    deepgram_url = f'{kwargs["host"]}/v1/listen?punctuate=true'

    if kwargs["model"]:
        deepgram_url += f"&model={kwargs['model']}"

    if kwargs["tier"]:
        deepgram_url += f"&tier={kwargs['tier']}"

    if kwargs["method"] == "blackhole":
        deepgram_url += "&encoding=linear16&sample_rate=16000"

    # Connect to the real-time streaming endpoint, attaching our credentials.
    async with websockets.connect(
        deepgram_url, extra_headers={"Authorization": f"Token {key}"}
    ) as ws:
        #print(f'ℹ️  Request ID: {ws.response_headers.get("dg-request-id")}')
        if kwargs["model"]:
            print(f'ℹ️  Model: {kwargs["model"]}')
        if kwargs["tier"]:
            print(f'ℹ️  Tier: {kwargs["tier"]}')
        #print("🟢 (1/5) Successfully opened Deepgram streaming connection")

        async def sender(ws):
            #print(
                #f'🟢 (2/5) Ready to stream system audio via BlackHole to Deepgram'
            #)

            try:
                while True:
                    audio_data = await audio_queue.get()
                    all_audio_data.append(audio_data)
                    await ws.send(audio_data)
            except websockets.exceptions.ConnectionClosedOK:
                await ws.send(json.dumps({"type": "CloseStream"}))
                #print(
                    #"🟢 (5/5) Successfully closed Deepgram connection, waiting for final transcripts if necessary"
                #)

            except Exception as e:
                print(f"Error while sending: {str(e)}")
                raise

        async def receiver(ws):
            """Print out the messages received from the server."""
            first_message = True
            first_transcript = True
            transcript = ""

            async for msg in ws:
                res = json.loads(msg)
                if first_message:
                    #print(
                        #"🟢 (3/5) Successfully receiving Deepgram messages, waiting for finalized transcription..."
                    #)
                    first_message = False
                try:
                    # handle local server messages
                    if res.get("msg"):
                        print(res["msg"])
                    if res.get("is_final"):
                        transcript = (
                            res.get("channel", {})
                            .get("alternatives", [{}])[0]
                            .get("transcript", "")
                        )
                        if kwargs["timestamps"]:
                            words = res.get("channel", {}).get("alternatives", [{}])[0].get("words", [])
                            start = words[0]["start"] if words else None
                            end = words[-1]["end"] if words else None
                            transcript += " [{} - {}]".format(start, end) if (start and end) else ""
                        if transcript != "":
                            if first_transcript:
                                #print("🟢 (4/5) Began receiving transcription")
                                # if using webvtt, print out header
                                if format == "vtt":
                                    print("WEBVTT\n")
                                first_transcript = False
                            if format == "vtt" or format == "srt":
                                transcript = subtitle_formatter(res, format)
                            #print(transcript)
                            all_transcripts.append(transcript)

                        await callback(transcript)  # Pass the transcript to the callback function

                    # handle end of stream
                    if res.get("created"):
                        # save subtitle data if specified
                        if format in ("vtt", "srt"):
                            data_dir = os.path.abspath(os.path.join(os.path.curdir, "data"))
                            if not os.path.exists(data_dir):
                                os.makedirs(data_dir)

                            transcript_file_path = os.path.abspath(
                                os.path.join(data_dir, f"{startTime.strftime('%Y%m%d%H%M')}.{format}")
                            )
                            with open(transcript_file_path, "w") as f:
                                f.write("".join(all_transcripts))
                            print(f"🟢 Subtitles saved to {transcript_file_path}")

                            # also save audio data if we were live streaming audio
                            if kwargs["method"] == "blackhole":
                                wave_file_path = os.path.abspath(
                                    os.path.join(data_dir, f"{startTime.strftime('%Y%m%d%H%M')}.wav")
                                )
                                wave_file = wave.open(wave_file_path, "wb")
                                wave_file.setnchannels(CHANNELS)
                                wave_file.setsampwidth(SAMPLE_SIZE)
                                wave_file.setframerate(RATE)
                                wave_file.writeframes(b"".join(all_audio_data))
                                wave_file.close()
                                print(f"🟢 Audio saved to {wave_file_path}")

                        print(
                            f'🟢 Request finished with a duration of {res["duration"]} seconds. Exiting!'
                        )
                except KeyError:
                    print(f"🔴 ERROR: Received unexpected API response! {msg}")

        # Set up BlackHole streaming
        async def blackhole():
            audio = pyaudio.PyAudio()
            stream = audio.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
                input_device_index=BLACKHOLE_DEVICE_INDEX,
                stream_callback=blackhole_callback,
            )

            stream.start_stream()

            global SAMPLE_SIZE
            SAMPLE_SIZE = audio.get_sample_size(FORMAT)

            while stream.is_active():
                await asyncio.sleep(0.1)

            stream.stop_stream()
            stream.close()

        functions = [
            asyncio.ensure_future(sender(ws)),
            asyncio.ensure_future(receiver(ws)),
            asyncio.ensure_future(blackhole()),  # Automatically include BlackHole streaming
        ]

        await asyncio.gather(*functions)

async def receive_transcriptions(callback):
    key = ""
    #key = os.getenv("DEEPGRAM_API_KEY")
    input_method = "blackhole"
    format = "text"
    host = "wss://api.deepgram.com"

    try:
        await run(callback, key, format, method=input_method, model="nova", tier=None, host=host, timestamps=False)
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    def print_transcript(transcript):
        print(f"Transcript: {transcript}")

    asyncio.run(receive_transcriptions(print_transcript))
