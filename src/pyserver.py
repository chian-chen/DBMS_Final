import socketserver
import clip
import torch
from torchvision.datasets import CIFAR100
from torchvision.utils import save_image
from PIL import Image  
import os
def clip_api(path):
    device = "cpu"
    model, preprocess = clip.load('ViT-B/32', device, download_root="/mysqludf/cache/clip")
    cifar100 = CIFAR100(root=os.path.expanduser("/mysqludf/cache"), download=True)
    image = Image.open(path)
    image_input = preprocess(image).unsqueeze(0).to(device)
    text_inputs = torch.cat([clip.tokenize(f"a photo of a {c}") for c in cifar100.classes]).to(device)
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
    return indices[0].item()

class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data =  self.request.recv(1024).decode().split(":")
        if data[0] == "path":
            path = data[1]
            path = bytes(path.encode())[:-1].decode()
            result = clip_api(path)
            self.request.sendall(str(result).encode())
        elif data[0] == "sim":
            path = data[1]

            path = bytes(path.encode())[:-1].decode()
            path_col = path.split("_")[0]
            path_query = path.split("_")[1]
            print(path_col)
            print(path_query)
            device = "cpu"
            model, preprocess = clip.load('ViT-B/32', device, download_root="/mysqludf/cache/clip")
            
            image_col = Image.open(path_col)
            image_query = Image.open(path_query)
            
            image_col = preprocess(image_col).unsqueeze(0).to(device)
            image_query = preprocess(image_query).unsqueeze(0).to(device)

            with torch.no_grad():
                col_features = model.encode_image(image_col)
                query_features = model.encode_image(image_query)

            col_features /= col_features.norm(dim=-1, keepdim=True)
            query_features /= query_features.norm(dim=-1, keepdim=True)
            similarity = (100.0 * col_features @ query_features.T)
            # print(similarity)

            result = int(similarity.item())
            print(result)
            self.request.sendall(str(result).encode())


# 创建服务器，绑定 IP 地址和端口号
HOST, PORT = "localhost", 9999
server = socketserver.ThreadingTCPServer((HOST, PORT), MyTCPHandler)

# 启动服务器
try:
    server.serve_forever()
except:
    server.server_close()
    print("Server closed.")

if __name__=="__main__":
    path = "/mysqludf/img.png_/mysqludf/img.png"
    path_col = path.split("_")[0]
    path_query = path.split("_")[1]

    device = "cpu"
    model, preprocess = clip.load('ViT-B/32', device, download_root="/mysqludf/cache/clip")
    
    image_col = Image.open(path_col)
    image_query = Image.open(path_query)
    
    image_col = preprocess(image_col).unsqueeze(0).to(device)
    image_query = preprocess(image_query).unsqueeze(0).to(device)

    with torch.no_grad():
        col_features = model.encode_image(image_col)
        query_features = model.encode_image(image_query)

    col_features /= col_features.norm(dim=-1, keepdim=True)
    query_features /= query_features.norm(dim=-1, keepdim=True)
    similarity = (100.0 * col_features @ query_features.T).item()
    print(similarity)
