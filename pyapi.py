import sys
# sys.path.append
# sys.path = ['/home/fourcolor/Documents/db112/final', '/usr/lib/python310.zip', '/usr/lib/python3.10', '/usr/lib/python3.10/lib-dynload', '/home/fourcolor/.local/lib/python3.10/site-packages', '/usr/local/lib/python3.10/dist-packages', '/usr/local/lib/python3.10/dist-packages/MobileInsight-6.0.0-py3.10-linux-x86_64.egg', '/home/fourcolor/Documents/p4-utils', '/usr/lib/python3/dist-packages', '/usr/lib/python3/dist-packages/bcc-0.28.0+bc9b43a0-py3.10.egg']
import os
import clip
import torch
from torchvision.datasets import CIFAR100
from torchvision.utils import save_image
from PIL import Image  
import PIL

def api(path):
    device =  "cpu"
    model, preprocess = clip.load('ViT-B/32', device)
    cifar100 = CIFAR100(root=os.path.expanduser("~/.cache"), download=True)
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
    print("\nTop predictions:\n")
    for value, index in zip(values, indices):
        print(f"{cifar100.classes[index]:>16s}: {100 * value.item():.2f}%")


api("img.png")