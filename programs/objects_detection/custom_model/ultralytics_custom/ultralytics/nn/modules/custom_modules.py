import torch
import torch.nn as nn
from ultralytics.nn.modules.conv import Conv
from ultralytics.nn.modules.head import Detect


class LocalContextAttention(nn.Module):
    """
    Hailo-friendly attention:
    DW conv (local context) -> PW reduce -> PW expand -> sigmoid gate.
    No GAP, no Linear.
    """

    def __init__(self, c: int, k: int = 3, r: int = 8):
        super().__init__()
        if not isinstance(k, int):
            raise TypeError(f"k must be int, got {type(k)}")
        if k % 2 == 0:
            raise ValueError(f"k must be odd to preserve spatial size, got k={k}")

        hidden = max(1, c // r)

        self.dw = nn.Conv2d(
            c, c, kernel_size=k, stride=1, padding=k // 2,
            groups=c, bias=False
        )
        self.dw_bn = nn.BatchNorm2d(c)
        self.dw_act = nn.SiLU(inplace=False)

        self.pw_reduce = nn.Conv2d(c, hidden, kernel_size=1, bias=False)
        self.pw_reduce_bn = nn.BatchNorm2d(hidden)
        self.pw_reduce_act = nn.SiLU(inplace=False)

        self.pw_expand = nn.Conv2d(hidden, c, kernel_size=1, bias=True)
        self.gate = nn.Sigmoid()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        y = self.dw_act(self.dw_bn(self.dw(x)))
        y = self.pw_reduce_act(self.pw_reduce_bn(self.pw_reduce(y)))
        g = self.gate(self.pw_expand(y))  # same H,W as x (if k is odd)
        return x * (1.0 + g)


class LCA(nn.Module):
    """
    Pure attention layer (no extra Conv). IMPORTANT: Ultralytics will call it as LCA(c1, c2, ...).
    We ignore c1 and use c2 as channel count (usually c1==c2 in your design).
    """

    def __init__(self, c1: int, c2: int = None, k: int = 3, r: int = 8):
        super().__init__()
        c = c2 if c2 is not None else c1
        self.attn = LocalContextAttention(c, k=k, r=r)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.attn(x).contiguous()


class ConvLCA(nn.Module):
    """
    Conv + LCA.
    """

    def __init__(self, c1, c2, k=3, s=1, p=None, g=1, act=True, attn_k: int = 3, attn_r: int = 8):
        super().__init__()
        self.conv = Conv(c1, c2, k, s, p, g, act=act)
        self.lca = LocalContextAttention(c2, k=attn_k, r=attn_r)

    def forward(self, x):
        return self.lca(self.conv(x)).contiguous()


class Detect_HailoFriendly(Detect):
    """
    Same as you had: normal Detect in runtime, split outputs in export.
    """

    def __init__(self, nc=14, ch=()):
        super().__init__(nc, ch)

    def forward(self, x):
        if torch.onnx.is_in_onnx_export() or getattr(self, "export", False):
            return self.forward_hailo_export(x)
        return super().forward(x)

    def forward_hailo_export(self, x):
        outputs = []
        for i in range(self.nl):
            bbox = self.cv2[i](x[i]).contiguous()
            cls = self.cv3[i](x[i]).contiguous()
            outputs.append(bbox)
            outputs.append(cls)
        return tuple(outputs)
