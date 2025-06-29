import tempfile
from pathlib import Path

import gradio as gr
import mediapy
import numpy as np
from PIL import Image

from eval import interpolator, util


def load_model(model_name: str, align: int, block_h: int, block_w: int):
    model_path = f"pretrained_models/film_net/{model_name}/saved_model"
    if align <= 1:
        align = None
    block_shape = [block_h, block_w]
    if block_h <= 1 and block_w <= 1:
        block_shape = None
    return interpolator.Interpolator(model_path, align=align, block_shape=block_shape)


def interpolate_frames(
    img1: Image.Image,
    img2: Image.Image,
    model_name: str = "Style",
    times: int = 1,
    align: int = 64,
    block_h: int = 1,
    block_w: int = 1,
):
    w = min(img1.width, img2.width)
    h = min(img1.height, img2.height)
    img1 = img1.crop((0, 0, w, h))
    img2 = img2.crop((0, 0, w, h))

    img1_np = np.array(img1).astype(np.float32) / 255.0
    img2_np = np.array(img2).astype(np.float32) / 255.0

    inter = load_model(model_name, align, block_h, block_w)
    if times == 1:
        dt = np.full((1,), 0.5, dtype=np.float32)
        out = inter(img1_np[None, ...], img2_np[None, ...], dt)[0]
        out_path = Path(tempfile.mkdtemp()) / "out.png"
        util.write_image(str(out_path), out)
        return out_path

    frames = list(
        util.interpolate_recursively_from_memory(
            [img1_np, img2_np], times, inter
        )
    )
    mediapy.set_ffmpeg(util.get_ffmpeg_path())
    out_path = Path(tempfile.mkdtemp()) / "out.mp4"
    mediapy.write_video(str(out_path), frames, fps=30)
    return out_path


def main():
    with gr.Blocks() as demo:
        gr.Markdown("# FILM Frame Interpolation")
        with gr.Row():
            in1 = gr.Image(label="Image 1", type="pil")
            in2 = gr.Image(label="Image 2", type="pil")
        model = gr.Dropdown(["Style", "L1", "VGG"], value="Style", label="Model")
        times = gr.Slider(1, 8, step=1, value=1, label="Times to Interpolate")
        align = gr.Slider(0, 128, step=1, value=64, label="Align (0 to disable)")
        block_h = gr.Slider(1, 4, step=1, value=1, label="Block Height")
        block_w = gr.Slider(1, 4, step=1, value=1, label="Block Width")
        out_file = gr.File(label="Output")
        run = gr.Button("Run")
        run.click(
            interpolate_frames,
            inputs=[in1, in2, model, times, align, block_h, block_w],
            outputs=out_file,
        )
    demo.launch()


if __name__ == "__main__":
    main()
