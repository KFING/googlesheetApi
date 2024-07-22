from pytubefix import YouTube

yt = YouTube("https://www.youtube.com/watch?v=VDEXD3LSOGU&list=PLq_oyKAUI5M_KSvG803Qd8ew53Uh-Y8LM")

audio = yt.streams.get_audio_only().download()