import schwabdev
#import stream

client = schwabdev.Client(app_key="n3uMFJH8tsA9z2SB2ag0sqNUNm4uPjai", app_secret="h9YybKHnDVoDM1Jw")

#client.update_tokens_auto()

#print(client.quotes('AMD').json())

streamer = client.stream

def response_handler(response):
    print(response)

streamer.start(response_handler)

streamer.send(streamer.level_one_equities("AMD", "0,1,2,3,4,5"))

import time
time.sleep(10)  # Keep the script running for a while to receive data   
