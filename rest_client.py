from score import Score
import requests

def bpm(bpm: int):
    requests.get('http://localhost:8000/bpm/' + str(bpm))

def reset():
    requests.get('http://localhost:8000/queue/reset')

def play(note: float, synth_name: str, sustain: float = 1.0):
    json_stuff = {}
    json_stuff["synth"] = synth_name
    json_stuff["values"] = []
    def new_val(name: str, value: float):
        json_stuff["values"].append({"name": name, "value": value})

    new_val("freq", note)
    new_val("amp", 1.0)
    new_val("sus", sustain)

    requests.post('http://localhost:5000/impl/s_new', json=json_stuff)
    # e.g. {'att': 0.2}
def tweak(synth_name: str, values):
    rep = requests.post('http://localhost:5000/impl/tweak/' + synth_name, json=values)
    print(str(rep))

def post_prosc(name: str, key: str, notes: list):
    response = requests.post(
        'http://localhost:8000/queue/prosc/'+ key + '/' + name,
        json=notes
    )
