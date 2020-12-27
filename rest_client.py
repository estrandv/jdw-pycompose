from score import Score
import requests

def bpm(bpm: int):
    requests.get('http://localhost:8000/bpm/' + str(bpm))

def reset():
    requests.get('http://localhost:8000/queue/reset')