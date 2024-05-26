import socketserver
import clip
import torch
from PIL import Image  
import os
def clip_api(path):
    print(path)
    class_names = ["airliner", "sports_car", "hummingbird", "Egyptian_cat", "Ox"
                "golden_retriever", "tailed_frog", "zebra", "container_ship", "trailer_truck"
                ]
    device = "cpu"
    model, preprocess = clip.load('ViT-B/32', device, download_root="/mysqludf/cache/clip")
    image = Image.open(path)
    image_input = preprocess(image).unsqueeze(0).to(device)
    text_inputs = torch.cat([clip.tokenize(f"a photo of a {c}") for c in class_names]).to(device)
    # Calculate features
    with torch.no_grad():
        image_features = model.encode_image(image_input)
        text_features = model.encode_text(text_inputs)

    # Pick the top 5 most similar labels for the image
    image_features /= image_features.norm(dim=-1, keepdim=True)
    text_features /= text_features.norm(dim=-1, keepdim=True)
    similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)
    values, indices = similarity[0].topk(5)

    # Print the result
    return str(indices[0].item() + 1) + '/' + str(indices[1].item() + 1) + '/' + str(indices[2].item() + 1)

class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data =  self.request.recv(1024).decode().split(":")
        if data[0] == "path":
            print(data)
            path = data[1]
            path = bytes(path.encode())[:-1].decode()
            result = clip_api(path)
            print(result)
            self.request.sendall(str(result).encode())
        

HOST, PORT = "localhost", 9999
server = socketserver.ThreadingTCPServer((HOST, PORT), MyTCPHandler)

server.serve_forever()