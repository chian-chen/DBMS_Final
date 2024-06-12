import socketserver
import clip
import torch
from torchvision.datasets import CIFAR100
from torchvision.utils import save_image
from PIL import Image  
import os
def clip_api(path):
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


# Function to convert PIL Image to numpy array
def pil_to_np(image):
    return np.array(image).astype(np.float32) / 255.0

# Function to calculate PSNR
def calculate_psnr(image_col, image_query):
    image_col_np = pil_to_np(image_col.resize((224, 224)))
    image_query_np = pil_to_np(image_query.resize((224, 224)))
    psnr_value = peak_signal_noise_ratio(image_col_np, image_query_np)
    return psnr_value

# Function to calculate SSIM
def calculate_ssim(image_col, image_query):
    image_col_np = pil_to_np(image_col.resize((224, 224)))
    image_query_np = pil_to_np(image_query.resize((224, 224)))
    # ssim_value = structural_similarity(image_col_np, image_query_np, channel_axis=-1)
    # # ssim_value = structural_similarity(image_col_np, image_query_np, multichannel=True)
    # return ssim_value

    K1 = 0.01
    K2 = 0.03
    L = 1  # The dynamic range of pixel values (255 for 8-bit grayscale images)

    C1 = (K1 * L) ** 2
    C2 = (K2 * L) ** 2

    mu_x = gaussian_filter(image_col_np, sigma=1.5)
    mu_y = gaussian_filter(image_query_np, sigma=1.5)

    mu_x_mu_y = mu_x * mu_y
    mu_x_sq = mu_x * mu_x
    mu_y_sq = mu_y * mu_y

    sigma_x = gaussian_filter(image_col_np * image_col_np, sigma=1.5) - mu_x_sq
    sigma_y = gaussian_filter(image_query_np * image_query_np, sigma=1.5) - mu_y_sq
    sigma_xy = gaussian_filter(image_col_np * image_query_np, sigma=1.5) - mu_x_mu_y

    numerator1 = 2 * mu_x_mu_y + C1
    numerator2 = 2 * sigma_xy + C2
    denominator1 = mu_x_sq + mu_y_sq + C1
    denominator2 = sigma_x + sigma_y + C2

    ssim_map = (numerator1 * numerator2) / (denominator1 * denominator2)
    ssim_value = ssim_map.mean()

    return ssim_value

# Function to calculate LPIPS
def calculate_lpips(image_col, image_query):

    loss_fn = lpips.LPIPS(net='alex')
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    image_col_tensor = transform(image_col).unsqueeze(0)
    image_query_tensor = transform(image_query).unsqueeze(0)
    lpips_value = loss_fn(image_col_tensor, image_query_tensor)
    return lpips_value.item()

class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        print('hello')
        data =  self.request.recv(1024).decode().split(":")
        print(data)
        if data[0] == "path":
            path = data[1]
            path = bytes(path.encode())[:-1].decode()
            result = clip_api(path)
            self.request.sendall(str(result).encode())
        elif data[0] == "sim":
            path = data[1]

            path = bytes(path.encode())[:-1].decode()
            path_col = path.split("$")[0]
            path_query = path.split("$")[1]
            # print(path_col)
            # print(path_query)
            print(f"Col: {path_col}, Query: \"{path_query}\", Sim: ",end="")

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

        elif data[0] == "sim_str":
            path = data[1]

            path = bytes(path.encode())[:-1].decode()
            path_col = path.split("$")[0]
            text_query = path.split("$")[1]

            print(f"Col: {path_col}, Query: \"{text_query}\", Sim: ",end="")
            # print(text_query)
            device = "cpu"
            model, preprocess = clip.load('ViT-B/32', device, download_root="/mysqludf/cache/clip")
            
            image_col = Image.open(path_col)
            image_col = preprocess(image_col).unsqueeze(0).to(device)

            text_query = clip.tokenize([text_query]).to(device)

            with torch.no_grad():
                col_features = model.encode_image(image_col)
                query_features = model.encode_text(text_query)

            col_features /= col_features.norm(dim=-1, keepdim=True)
            query_features /= query_features.norm(dim=-1, keepdim=True)
            similarity = (100.0 * col_features @ query_features.T)
            # print(similarity)

            result = int(similarity.item())
            print(result)
            self.request.sendall(str(result).encode())
        
        elif data[0] in ["sim_psnr", "sim_ssim", "sim_lpips"]:
            method = data[0].split("_")[1]

            path = data[1]

            path = bytes(path.encode())[:-1].decode()
            path_col = path.split("$")[0]
            path_query = path.split("$")[1]
            # print(path_col)
            # print(path_query)
            print(f"Col: {path_col}, Query: \"{path_query}\", Sim: ",end="")

            image_col = Image.open(path_col)
            image_query = Image.open(path_query)

            if method == "psnr":
                result = calculate_psnr(image_col, image_query)
            elif method == "ssim":
                result = 100 * calculate_ssim(image_col, image_query)
            elif method == "lpips":
                result = 100 * calculate_lpips(image_col, image_query)
            print(result)
            self.request.sendall(str(result).encode())

        else:
            print(f"Unknown udf: {data[0]}")

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
    pass