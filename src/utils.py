import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms

from torch.nn.functional import softmax


def get_resnet18(num_classes):
    new_layers = nn.Sequential(
        nn.Linear(1000, 256),
        nn.Linear(256, 128),
        nn.Linear(128, num_classes)
    )
    backbone = models.resnet50(pretrained=True)
    net = nn.Sequential(backbone, new_layers)
    return net

def get_squeezenet(num_classes):
    backbone = models.squeezenet1_1(pretrained=True)
    backbone.num_classes = num_classes
    backbone.classifier = nn.Sequential(
        nn.Dropout(p=0.5),
        nn.Conv2d(512, num_classes, kernel_size=1),
        nn.ReLU(inplace=True),
        nn.AvgPool2d(13)
    )
    backbone.forward = lambda x: backbone.classifier(backbone.features(x)).view(x.size(0), 7)
    return backbone

def get_prediction(network, input_data, device):
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )
    face_tensor = transform(input_data)
    face_tensor = face_tensor.view(1, 3, 512, 512).float().to(device)
    with torch.no_grad():
        result = network(face_tensor).float()
        result.to('cpu')
    return softmax(result, dim=1)