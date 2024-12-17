from torch.nn import Module, Sequential, Conv2d, MaxPool2d, LeakyReLU, ConvTranspose2d, Sigmoid
from torchsummary import summary


class DummyNet(Module):
    def __init__(self, in_channels=3, classes=1):
        super().__init__()
        self.encoder = Sequential(
            Conv2d(in_channels, 32, 3, 1, 1),
            MaxPool2d(2, 2),
            LeakyReLU(),
        )

        self.decoder = Sequential(
            ConvTranspose2d(32, classes, 4, 2, 1),
            LeakyReLU(),
        )

        self.head = Sigmoid()

    def forward(self, x):
        x = self.encoder(x)
        x = self.decoder(x)
        x = self.head(x)
        return x


if __name__ == '__main__':
    summary(DummyNet(), (3, 256, 256))