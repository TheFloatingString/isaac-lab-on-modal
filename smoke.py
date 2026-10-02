"""Isaac Lab smoke test: load a task, step it, save a third-person camera PNG.

Runs inside the Modal image (see main.py). Isaac Lab modules can only be imported
after AppLauncher has started Kit, so all isaaclab imports live inside run_smoke().

    python smoke.py --task Isaac-Stack-Cube-Franka-v0 --out out.png \
        --eye 1.4 -1.0 1.1 --target 0.5 0.0 0.1
"""
import argparse

from isaaclab.app import AppLauncher


def run_smoke(task: str, out: str, eye: list[float], target: list[float], steps: int = 30) -> None:
    parser = argparse.ArgumentParser()
    AppLauncher.add_app_launcher_args(parser)
    simulation_app = AppLauncher(parser.parse_args(["--headless", "--enable_cameras"])).app

    import gymnasium as gym
    import numpy as np
    import torch
    from PIL import Image

    import isaaclab.sim as sim_utils
    import isaaclab_tasks  # noqa: F401
    from isaaclab.sensors import CameraCfg
    from isaaclab_tasks.utils.parse_cfg import parse_env_cfg

    cfg = parse_env_cfg(task, device="cuda:0", num_envs=1)
    cfg.scene.tp_cam = CameraCfg(
        prim_path="{ENV_REGEX_NS}/tp_cam",
        update_period=0.0,
        height=480,
        width=640,
        data_types=["rgb"],
        spawn=sim_utils.PinholeCameraCfg(focal_length=18.0, horizontal_aperture=20.955, clipping_range=(0.1, 100.0)),
        offset=CameraCfg.OffsetCfg(pos=(0.0, 0.0, 0.0), rot=(1.0, 0.0, 0.0, 0.0), convention="world"),
    )
    env = gym.make(task, cfg=cfg)
    env.reset()
    u = env.unwrapped
    cam = u.scene["tp_cam"]
    origin = u.scene.env_origins[0]
    eyes = (origin + torch.tensor(eye, device=u.device)).unsqueeze(0)
    targets = (origin + torch.tensor(target, device=u.device)).unsqueeze(0)
    act = torch.zeros(u.action_space.shape, device=u.device)
    for _ in range(steps):
        cam.set_world_poses_from_view(eyes, targets)
        env.step(act)
    rgb = cam.data.output["rgb"][0].cpu().numpy()[..., :3].astype(np.uint8)
    print("task", task, "rgb shape", rgb.shape, "mean", rgb.mean(), "std", rgb.std())
    Image.fromarray(rgb).save(out)
    assert rgb.std() > 1.0, "image looks blank"
    print("SMOKE_OK")
    env.close()
    simulation_app.close()


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--task", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--eye", type=float, nargs=3, required=True)
    p.add_argument("--target", type=float, nargs=3, required=True)
    p.add_argument("--steps", type=int, default=30)
    a = p.parse_args()
    run_smoke(a.task, a.out, a.eye, a.target, a.steps)
