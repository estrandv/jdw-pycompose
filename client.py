from pythonosc.udp_client import SimpleUDPClient 

def get_default() -> SimpleUDPClient:
    return SimpleUDPClient("127.0.0.1", 13339) # Router