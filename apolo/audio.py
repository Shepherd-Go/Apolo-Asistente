import queue
import numpy as np
from apolo.config import VOZ_THRESHOLD, SILENCIO_LIMITE, MAX_BLOQUES

audio_queue: queue.Queue = queue.Queue()
grabando = False
silencio_cnt = 0
voz_buffer = []


def audio_callback(indata, frames, time_info, status):
    global grabando, silencio_cnt, voz_buffer

    rms = float(np.sqrt(np.mean(indata.astype(np.float32) ** 2))) / 32768

    if rms > VOZ_THRESHOLD:
        grabando = True
        silencio_cnt = 0
        voz_buffer.append(indata.copy())
    elif grabando:
        voz_buffer.append(indata.copy())
        silencio_cnt += 1
        if silencio_cnt >= SILENCIO_LIMITE or len(voz_buffer) >= MAX_BLOQUES:
            audio_queue.put(np.concatenate(voz_buffer, axis=0))
            voz_buffer = []
            grabando = False
            silencio_cnt = 0
