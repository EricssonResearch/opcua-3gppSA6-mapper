import cv2
import requests
import numpy as np

stream_url = "http://127.0.0.1:5000"

stream = requests.get(stream_url, stream=True)

cv2.namedWindow('Stream', cv2.WINDOW_NORMAL)

if stream.status_code == 200:

    bytes = b''
   
    for chunk in stream.iter_content(chunk_size=1024):
    
        bytes += chunk
        a = bytes.find(b'\xff\xd8')
        b = bytes.find(b'\xff\xd9')
        
        if a != -1 and b != -1:
        
            jpg = bytes[a:b+2]
            bytes = bytes[b+2:]
            img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
            cv2.imshow('Stream', img)
       
            if cv2.waitKey(1) == 27 or cv2.getWindowProperty('Stream', cv2.WND_PROP_VISIBLE) < 1:
                break

else:
    print("Unable to open stream")

cv2.destroyAllWindows()

