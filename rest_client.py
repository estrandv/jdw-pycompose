from score import Score
import requests

def bpm(bpm: int):
    requests.get('http://localhost:8000/bpm/' + str(bpm))

def reset():
    requests.get('http://localhost:8000/queue/reset')

# e.g. {'att': 0.2}
def tweak(synth_name: str, values):
    rep = requests.post('http://localhost:5000/impl/tweak/' + synth_name, json=values)
    print(str(rep))