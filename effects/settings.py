from __future__ import annotations

from dataclasses import asdict, dataclass, fields

PRESETS: dict[str, dict[str, float | bool]] = {
    "Clean": {},
    "16mm Film": {
        "contrast": 1.12,
        "saturation": 0.82,
        "vignette": 0.38,
        "grain": 0.42,
        "scanlines": 0.05,
        "chromatic": 0.06,
        "temperature": 0.08,
    },
    "VHS / Tape": {
        "contrast": 1.08,
        "saturation": 1.12,
        "vignette": 0.25,
        "grain": 0.34,
        "scanlines": 0.36,
        "chromatic": 0.52,
        "glitch": 0.28,
        "hue": -8.0,
    },
    "CRT": {
        "contrast": 1.18,
        "saturation": 0.92,
        "vignette": 0.58,
        "scanlines": 0.62,
        "pixelate": 0.16,
        "chromatic": 0.12,
    },
    "Bleach Bypass": {
        "contrast": 1.42,
        "saturation": 0.24,
        "gamma": 0.92,
        "vignette": 0.2,
        "exposure": -0.12,
    },
    "Dream Haze": {
        "brightness": 0.07,
        "contrast": 0.86,
        "saturation": 1.28,
        "gamma": 1.12,
        "chromatic": 0.18,
        "grain": 0.08,
        "temperature": 0.12,
        "tint": 0.08,
    },
    "Digital Damage": {
        "contrast": 1.22,
        "saturation": 1.18,
        "grain": 0.18,
        "scanlines": 0.12,
        "chromatic": 0.62,
        "glitch": 0.74,
        "pixelate": 0.08,
        "solarize": 0.12,
    },
    "Halftone Print": {
        "contrast": 1.28,
        "saturation": 0.18,
        "halftone": 0.78,
        "grain": 0.12,
        "posterize": 0.28,
        "vignette": 0.12,
    },
    "Photocopy": {
        "brightness": 0.08,
        "contrast": 1.72,
        "saturation": 0.0,
        "gamma": 0.82,
        "halftone": 0.44,
        "grain": 0.32,
        "posterize": 0.58,
    },
    "Infrared": {
        "contrast": 1.32,
        "saturation": 1.55,
        "hue": 128.0,
        "temperature": 0.42,
        "tint": -0.28,
        "chromatic": 0.12,
    },
    "Cold Steel": {
        "contrast": 1.18,
        "saturation": 0.78,
        "temperature": -0.46,
        "tint": -0.08,
        "gamma": 0.94,
        "vignette": 0.26,
    },
    "Solarized": {
        "contrast": 1.18,
        "saturation": 1.15,
        "solarize": 0.82,
        "hue": 18.0,
        "grain": 0.08,
    },
    "Sakura Fade": {
        "brightness": 0.035,
        "contrast": 0.94,
        "saturation": 0.72,
        "hue": -12.0,
        "tint": 0.08,
        "grain": 0.10,
    },
    "Noh Theatre": {
        "contrast": 1.45,
        "saturation": 0.12,
        "gamma": 0.86,
        "vignette": 0.36,
        "grain": 0.14,
    },
    "Indigo Night": {
        "contrast": 1.20,
        "saturation": 0.84,
        "hue": -14.0,
        "temperature": -0.25,
        "scanlines": 0.12,
    },
    "Shin-hanga": {
        "contrast": 1.12,
        "saturation": 1.16,
        "gamma": 1.04,
        "posterize": 0.12,
        "grain": 0.08,
    },
    "Kintsugi": {
        "contrast": 1.28,
        "saturation": 0.92,
        "temperature": 0.14,
        "tint": 0.12,
        "grain": 0.06,
        "chromatic": 0.04,
    },
}


@dataclass
class EffectSettings:
    """Master GPU post-processing controls shared by preview and projector output."""

    enabled: bool = True
    mix: float = 1.0
    brightness: float = 0.0
    exposure: float = 0.0
    contrast: float = 1.0
    saturation: float = 1.0
    gamma: float = 1.0
    temperature: float = 0.0
    tint: float = 0.0
    hue: float = 0.0
    vignette: float = 0.0
    grain: float = 0.0
    scanlines: float = 0.0
    chromatic: float = 0.0
    glitch: float = 0.0
    pixelate: float = 0.0
    posterize: float = 0.0
    invert: float = 0.0
    halftone: float = 0.0
    solarize: float = 0.0
    transform_mode: str = "none"
    transform_mix: float = 1.0
    kaleidoscope_slices: int = 8
    kaleidoscope_rotation: float = 0.0
    kaleidoscope_zoom: float = 1.0
    mosaic_tiles: int = 64
    pixel_sort_amount: float = 0.0
    pixel_sort_threshold: float = 0.72
    edge_amount: float = 0.0
    dither: float = 0.0
    displacement_source_id: str = ""
    displacement_amount: float = 0.0
    displacement_scale: float = 1.0
    displacement_luma: bool = False
    feedback_enabled: bool = False
    feedback_amount: float = 0.35
    feedback_decay: float = 0.94
    feedback_zoom: float = 1.0
    feedback_rotation: float = 0.0
    feedback_translate_x: float = 0.0
    feedback_translate_y: float = 0.0
    feedback_color_shift: float = 0.0
    feedback_distortion: float = 0.0
    feedback_motion_warp: float = 0.0
    feedback_datamosh: float = 0.0
    feedback_blend_mode: str = "normal"
    feedback_delay_frames: int = 0
    feedback_frozen: bool = False
    feedback_reset_generation: int = 0
    preset_name: str = "Clean"

    def apply_preset(self, name: str) -> None:
        if name not in PRESETS:
            raise KeyError(f"Unknown effect preset: {name}")
        self.reset()
        for field_name, value in PRESETS[name].items():
            setattr(self, field_name, value)
        self.preset_name = name
        self.clamp()

    def reset(self) -> None:
        # A generation bump invalidates renderer-local temporal feedback on its
        # next frame without exposing any GPU resources to the settings model.
        reset_generation = max(0, int(self.feedback_reset_generation)) + 1
        defaults = type(self)()
        for item in fields(self):
            setattr(self, item.name, getattr(defaults, item.name))
        self.feedback_reset_generation = reset_generation

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> EffectSettings:
        allowed = {item.name for item in fields(cls)}
        values = {key: value for key, value in data.items() if key in allowed}
        settings = cls(**values)
        settings.clamp()
        return settings

    def clamp(self) -> None:
        self.enabled = bool(self.enabled)
        self.mix = max(0.0, min(1.0, float(self.mix)))
        self.brightness = max(-0.5, min(0.5, float(self.brightness)))
        self.exposure = max(-2.0, min(2.0, float(self.exposure)))
        self.contrast = max(0.0, min(2.5, float(self.contrast)))
        self.saturation = max(0.0, min(2.5, float(self.saturation)))
        self.gamma = max(0.2, min(2.5, float(self.gamma)))
        self.temperature = max(-1.0, min(1.0, float(self.temperature)))
        self.tint = max(-1.0, min(1.0, float(self.tint)))
        self.hue = max(-180.0, min(180.0, float(self.hue)))
        for name in (
                "vignette",
                "grain",
                "scanlines",
                "chromatic",
                "glitch",
                "pixelate",
                "posterize",
                "invert",
                "halftone",
                "solarize",
        ):
            setattr(self, name, max(0.0, min(1.0, float(getattr(self, name)))))

        self.transform_mode = str(self.transform_mode).casefold()
        if self.transform_mode not in {
            "none", "kaleidoscope", "polar", "mosaic", "pixel_sort",
        }:
            self.transform_mode = "none"
        self.transform_mix = max(0.0, min(1.0, float(self.transform_mix)))
        self.kaleidoscope_slices = max(2, min(64, int(self.kaleidoscope_slices)))
        self.kaleidoscope_rotation = max(-180.0, min(180.0, float(self.kaleidoscope_rotation)))
        self.kaleidoscope_zoom = max(0.1, min(4.0, float(self.kaleidoscope_zoom)))
        self.mosaic_tiles = max(4, min(512, int(self.mosaic_tiles)))
        self.pixel_sort_amount = max(0.0, min(1.0, float(self.pixel_sort_amount)))
        self.pixel_sort_threshold = max(0.0, min(1.0, float(self.pixel_sort_threshold)))
        self.edge_amount = max(0.0, min(1.0, float(self.edge_amount)))
        self.dither = max(0.0, min(1.0, float(self.dither)))
        self.displacement_source_id = str(self.displacement_source_id or "").strip()[:256]
        self.displacement_amount = max(-1.0, min(1.0, float(self.displacement_amount)))
        self.displacement_scale = max(0.1, min(8.0, float(self.displacement_scale)))
        self.displacement_luma = bool(self.displacement_luma)
        self.feedback_enabled = bool(self.feedback_enabled)
        self.feedback_amount = max(0.0, min(1.0, float(self.feedback_amount)))
        self.feedback_decay = max(0.0, min(1.0, float(self.feedback_decay)))
        self.feedback_zoom = max(0.5, min(2.0, float(self.feedback_zoom)))
        self.feedback_rotation = max(-180.0, min(180.0, float(self.feedback_rotation)))
        self.feedback_translate_x = max(-0.25, min(0.25, float(self.feedback_translate_x)))
        self.feedback_translate_y = max(-0.25, min(0.25, float(self.feedback_translate_y)))
        for name in (
                "feedback_color_shift",
                "feedback_distortion",
                "feedback_motion_warp",
                "feedback_datamosh",
        ):
            setattr(self, name, max(0.0, min(1.0, float(getattr(self, name)))))
        self.feedback_blend_mode = str(self.feedback_blend_mode).casefold()
        if self.feedback_blend_mode not in {
            "normal", "add", "screen", "multiply", "difference",
        }:
            self.feedback_blend_mode = "normal"
        self.feedback_delay_frames = max(0, min(3, int(self.feedback_delay_frames)))
        self.feedback_frozen = bool(self.feedback_frozen)
        self.feedback_reset_generation = max(0, int(self.feedback_reset_generation))
