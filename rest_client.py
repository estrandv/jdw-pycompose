from score import Score
import requests

def bpm(bpm: int):
    requests.get('http://localhost:8000/bpm/' + str(bpm))

def reset():
    requests.get('http://localhost:8000/queue/reset')

def play(note: float, synth_name: str):
    json_stuff = {}
    args = [synth_name, -1, 0, 0, "freq", note, "amp", 1.0, "sus", 1.0]
    json_stuff['args'] = args 
    requests.post('http://localhost:5000/osc/s_new', json=json_stuff)
    # e.g. {'att': 0.2}
def tweak(synth_name: str, values):
    rep = requests.post('http://localhost:5000/impl/tweak/' + synth_name, json=values)
    print(str(rep))
