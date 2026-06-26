#!/usr/bin/env python3
"""Architecture-only reference implementation of RAAF-BiPAC-Mamba.

This file is provided to document the model structure described in the
manuscript. It intentionally contains no data loader, training loop, file
paths, normalization statistics, checkpoint loading, or private run metadata.

Inputs expected by ``RAAFBiPACMamba.forward``:
    vibration: [batch, 1, 2048]
    acoustic:  [batch, 1, 2048]

Label convention used by the PAC helper functions:
    0 = coal, 1 = gangue, 2 = empty

The model requires PyTorch and the official ``mamba_ssm`` package if users want
to instantiate it. The rest of the public reproducibility package remains
standard-library based and does not import this file during package validation.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Tuple

import torch
from torch import Tensor, nn
from torch.autograd import Function

try:
    from mamba_ssm import Mamba
except ImportError as exc:  # pragma: no cover - optional architecture dependency
    Mamba = None
    _MAMBA_IMPORT_ERROR = exc
else:
    _MAMBA_IMPORT_ERROR = None


CLASS_TO_INDEX = {"coal": 0, "gangue": 1, "empty": 2}


class GradientReversal(Function):
    """Gradient reversal layer used for adversarial noise-scenario alignment."""

    @staticmethod
    def forward(ctx, x: Tensor, alpha: float) -> Tensor:
        ctx.alpha = float(alpha)
        return x.view_as(x)

    @staticmethod
    def backward(ctx, grad_output: Tensor) -> Tuple[Tensor, None]:
        return -ctx.alpha * grad_output, None


class GRLLayer(nn.Module):
    """Module wrapper around ``GradientReversal``."""

    def __init__(self, alpha: float = 0.0) -> None:
        super().__init__()
        self.alpha = float(alpha)

    def forward(self, x: Tensor) -> Tensor:
        return GradientReversal.apply(x, self.alpha)


def grl_sigmoid_coefficient(progress: float, cap: float = 0.3) -> float:
    """Sigmoid GRL schedule capped as described in the manuscript.

    ``progress`` should be in [0, 1]. The returned value is capped at 0.3 by
    default because the manuscript reports a capped sigmoid GRL coefficient.
    """

    p = min(max(float(progress), 0.0), 1.0)
    value = 2.0 / (1.0 + math.exp(-10.0 * p)) - 1.0
    return min(float(cap), value)


class ResNetStem(nn.Module):
    """Convolutional stem that maps one 2048-point stream to 512 tokens.

    With the default kernel size and stride, an input length of 2048 becomes
    L' = 512, matching the manuscript's downsampled token length.
    """

    def __init__(self, in_channels: int = 1, out_channels: int = 64) -> None:
        super().__init__()
        self.main_path = nn.Sequential(
            nn.Conv1d(in_channels, out_channels, kernel_size=4, stride=4, padding=0),
            nn.BatchNorm1d(out_channels),
            nn.ReLU(),
            nn.Conv1d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm1d(out_channels),
        )
        self.shortcut = nn.Sequential(
            nn.Conv1d(in_channels, out_channels, kernel_size=4, stride=4, padding=0),
            nn.BatchNorm1d(out_channels),
        )
        self.activation = nn.ReLU()

    def forward(self, x: Tensor) -> Tensor:
        return self.activation(self.main_path(x) + self.shortcut(x))


class BidirectionalMambaBlock(nn.Module):
    """Bidirectional selective-SSM block with independent directions.

    This follows the manuscript equations:

    F_fwd = Mamba_fwd(LN(H))
    F_bwd = Flip(Mamba_bwd(LN(Flip(H))))
    F = H + Dropout(F_fwd + F_bwd)
    """

    def __init__(
        self,
        d_model: int = 64,
        d_state: int = 16,
        d_conv: int = 4,
        expand: int = 2,
        dropout: float = 0.10,
    ) -> None:
        super().__init__()
        if Mamba is None:
            raise ImportError(
                "RAAFBiPACMamba requires the optional package 'mamba_ssm' "
                "to instantiate the selective-SSM blocks."
            ) from _MAMBA_IMPORT_ERROR

        self.norm_fwd = nn.LayerNorm(d_model)
        self.norm_bwd = nn.LayerNorm(d_model)
        self.mamba_fwd = Mamba(
            d_model=d_model,
            d_state=d_state,
            d_conv=d_conv,
            expand=expand,
        )
        self.mamba_bwd = Mamba(
            d_model=d_model,
            d_state=d_state,
            d_conv=d_conv,
            expand=expand,
        )
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: Tensor) -> Tensor:
        y_fwd = self.mamba_fwd(self.norm_fwd(x))
        x_rev = torch.flip(x, dims=[1])
        y_bwd = self.mamba_bwd(self.norm_bwd(x_rev))
        y_bwd = torch.flip(y_bwd, dims=[1])
        return x + self.dropout(y_fwd + y_bwd)


class CrossAttention(nn.Module):
    """Four-head cross-modal attention."""

    def __init__(self, dim: int = 64, num_heads: int = 4) -> None:
        super().__init__()
        if dim % num_heads != 0:
            raise ValueError("dim must be divisible by num_heads")
        self.num_heads = num_heads
        self.head_dim = dim // num_heads
        self.scale = self.head_dim ** -0.5
        self.q_proj = nn.Linear(dim, dim)
        self.k_proj = nn.Linear(dim, dim)
        self.v_proj = nn.Linear(dim, dim)
        self.out_proj = nn.Linear(dim, dim)

    def forward(self, query_sequence: Tensor, key_value_sequence: Tensor) -> Tensor:
        batch, length, dim = query_sequence.shape
        q = self.q_proj(query_sequence).reshape(
            batch, length, self.num_heads, self.head_dim
        ).transpose(1, 2)
        k = self.k_proj(key_value_sequence).reshape(
            batch, length, self.num_heads, self.head_dim
        ).transpose(1, 2)
        v = self.v_proj(key_value_sequence).reshape(
            batch, length, self.num_heads, self.head_dim
        ).transpose(1, 2)

        attn = (q @ k.transpose(-2, -1) * self.scale).softmax(dim=-1)
        out = (attn @ v).transpose(1, 2).reshape(batch, length, dim)
        return self.out_proj(out)


def latent_vibration_roughness(vibration_sequence: Tensor) -> Tensor:
    """Compute R_vib from the post-cross-attention vibration sequence.

    This is the differentiable statistic in the manuscript:
    mean(abs(A_vib[t + 1, d] - A_vib[t, d])) over time and feature channels.
    """

    diff = vibration_sequence[:, 1:, :] - vibration_sequence[:, :-1, :]
    return diff.abs().mean(dim=(1, 2))


class RoughnessAwareAdaptiveFusion(nn.Module):
    """Roughness-aware adaptive fusion (RAAF).

    The same R_vib scalar computed from the post-cross-attention vibration
    sequence is used both for fusion gating and for PAC regularization.
    """

    def __init__(self, dim: int = 64, hidden_dim: int | None = None) -> None:
        super().__init__()
        hidden = hidden_dim or dim
        self.pool = nn.AdaptiveAvgPool1d(1)
        self.gate = nn.Sequential(
            nn.Linear(dim * 2 + 1, hidden),
            nn.ReLU(),
            nn.Linear(hidden, 2),
        )

    def forward(
        self,
        acoustic_sequence: Tensor,
        vibration_sequence: Tensor,
    ) -> Tuple[Tensor, Tensor, Tensor]:
        acoustic_pool = self.pool(acoustic_sequence.transpose(1, 2)).squeeze(-1)
        vibration_pool = self.pool(vibration_sequence.transpose(1, 2)).squeeze(-1)
        roughness = latent_vibration_roughness(vibration_sequence)

        gate_input = torch.cat(
            [acoustic_pool, vibration_pool, roughness.unsqueeze(1)],
            dim=1,
        )
        weights = torch.softmax(self.gate(gate_input), dim=1)
        acoustic_weight = weights[:, 0:1]
        vibration_weight = weights[:, 1:2]
        fused = torch.cat(
            [acoustic_weight * acoustic_pool, vibration_weight * vibration_pool],
            dim=1,
        )
        return fused, weights, roughness


@dataclass(frozen=True)
class PACThresholds:
    """Fixed PAC thresholds estimated from training-split roughness values."""

    tau_low: float
    tau_gangue: float
    mu_low: float
    sigma_low: float
    mu_gangue: float
    sigma_gangue: float


def estimate_pac_thresholds(
    roughness: Tensor,
    labels: Tensor,
    k: float = 0.5,
) -> PACThresholds:
    """Estimate PAC thresholds from training-split roughness values only.

    Coal and empty define the low-roughness group; gangue defines the
    high-roughness group. If the two thresholds cross, both are set to the
    midpoint between the group means, as stated in the manuscript.
    """

    rough = roughness.detach().float().reshape(-1)
    y = labels.detach().reshape(-1)
    low = rough[y != CLASS_TO_INDEX["gangue"]]
    gangue = rough[y == CLASS_TO_INDEX["gangue"]]
    if low.numel() == 0 or gangue.numel() == 0:
        raise ValueError("Both low-roughness and gangue groups are required.")

    mu_low = low.mean()
    sigma_low = low.std(unbiased=False)
    mu_gangue = gangue.mean()
    sigma_gangue = gangue.std(unbiased=False)
    tau_low = mu_low + float(k) * sigma_low
    tau_gangue = mu_gangue - float(k) * sigma_gangue
    if tau_low > tau_gangue:
        midpoint = 0.5 * (mu_low + mu_gangue)
        tau_low = midpoint
        tau_gangue = midpoint

    return PACThresholds(
        tau_low=float(tau_low.item()),
        tau_gangue=float(tau_gangue.item()),
        mu_low=float(mu_low.item()),
        sigma_low=float(sigma_low.item()),
        mu_gangue=float(mu_gangue.item()),
        sigma_gangue=float(sigma_gangue.item()),
    )


def pac_loss(
    roughness: Tensor,
    labels: Tensor,
    tau_low: float,
    tau_gangue: float,
    empty_constrained: bool = True,
) -> Tensor:
    """One-sided label-conditioned PAC roughness loss.

    Default manuscript rule:
        coal and empty samples are penalized above tau_low;
        gangue samples are penalized below tau_gangue.

    Set ``empty_constrained=False`` for the empty-unconstrained PAC-GRL control:
        coal is constrained as low roughness, gangue as high roughness, and
        empty remains a supervised recognition class without a PAC margin term.
    """

    y = labels.reshape(-1)
    rough = roughness.reshape(-1)
    if empty_constrained:
        low_mask = y != CLASS_TO_INDEX["gangue"]
    else:
        low_mask = y == CLASS_TO_INDEX["coal"]
    gangue_mask = y == CLASS_TO_INDEX["gangue"]

    low_penalty = torch.relu(rough - float(tau_low)) * low_mask.to(rough.dtype)
    gangue_penalty = torch.relu(float(tau_gangue) - rough) * gangue_mask.to(rough.dtype)
    return (low_penalty + gangue_penalty).mean()


class RAAFBiPACMamba(nn.Module):
    """RAAF-BiPAC-Mamba architecture described in the manuscript."""

    def __init__(
        self,
        num_classes: int = 3,
        num_noise_classes: int = 7,
        model_dim: int = 64,
        classifier_hidden: int = 128,
    ) -> None:
        super().__init__()
        self.stem_acoustic = ResNetStem(1, model_dim)
        self.stem_vibration = ResNetStem(1, model_dim)
        self.mamba_acoustic = BidirectionalMambaBlock(model_dim)
        self.mamba_vibration = BidirectionalMambaBlock(model_dim)
        self.cross_vibration_to_acoustic = CrossAttention(model_dim, num_heads=4)
        self.cross_acoustic_to_vibration = CrossAttention(model_dim, num_heads=4)
        self.raaf = RoughnessAwareAdaptiveFusion(model_dim)

        fused_dim = model_dim * 2
        self.material_classifier = nn.Sequential(
            nn.Linear(fused_dim, classifier_hidden),
            nn.BatchNorm1d(classifier_hidden),
            nn.ReLU(),
            nn.Dropout(0.30),
            nn.Linear(classifier_hidden, classifier_hidden // 2),
            nn.BatchNorm1d(classifier_hidden // 2),
            nn.ReLU(),
            nn.Linear(classifier_hidden // 2, num_classes),
        )
        self.grl = GRLLayer(alpha=0.0)
        self.noise_discriminator = nn.Sequential(
            nn.Linear(fused_dim, classifier_hidden // 2),
            nn.ReLU(),
            nn.Linear(classifier_hidden // 2, num_noise_classes),
        )

    def set_grl_alpha(self, alpha: float) -> None:
        """Set the GRL coefficient, typically from ``grl_sigmoid_coefficient``."""

        self.grl.alpha = float(alpha)

    def forward(self, vibration: Tensor, acoustic: Tensor) -> Dict[str, Tensor]:
        """Run the two-stream model.

        The returned dictionary exposes the intermediate tensors needed to
        compute RAAF diagnostics and PAC loss without including training code.
        """

        vibration_tokens = self.stem_vibration(vibration).transpose(1, 2)
        acoustic_tokens = self.stem_acoustic(acoustic).transpose(1, 2)

        m_vib = self.mamba_vibration(vibration_tokens)
        m_aud = self.mamba_acoustic(acoustic_tokens)

        a_aud = self.cross_vibration_to_acoustic(
            query_sequence=m_aud,
            key_value_sequence=m_vib,
        )
        a_vib = self.cross_acoustic_to_vibration(
            query_sequence=m_vib,
            key_value_sequence=m_aud,
        )

        fused, weights, roughness = self.raaf(a_aud, a_vib)
        material_logits = self.material_classifier(fused)
        noise_logits = self.noise_discriminator(self.grl(fused))
        return {
            "material_logits": material_logits,
            "noise_logits": noise_logits,
            "fused": fused,
            "raaf_weights": weights,
            "vibration_roughness": roughness,
            "post_attention_acoustic": a_aud,
            "post_attention_vibration": a_vib,
        }


# Backward-compatible alias used by retained local analysis scripts.
PAC_Mamba_MultiTask = RAAFBiPACMamba


__all__ = [
    "CLASS_TO_INDEX",
    "CrossAttention",
    "GRLLayer",
    "GradientReversal",
    "PACThresholds",
    "PAC_Mamba_MultiTask",
    "RAAFBiPACMamba",
    "ResNetStem",
    "RoughnessAwareAdaptiveFusion",
    "BidirectionalMambaBlock",
    "estimate_pac_thresholds",
    "grl_sigmoid_coefficient",
    "latent_vibration_roughness",
    "pac_loss",
]
