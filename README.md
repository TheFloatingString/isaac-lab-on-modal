# Isaac Lab on Modal

Smoke tests for [Isaac Lab](https://github.com/isaac-sim/IsaacLab) v2.3.0 (Isaac Sim 5.1.0) running on a Modal L40S GPU. Each test loads a task, steps it, and saves a third-person camera PNG.

## Run

```bash
pip install uv
uv sync
uv run modal setup
uv run modal run main.py --which franka   # Isaac-Stack-Cube-Franka-v0 -> stack_cube_franka.png
uv run modal run main.py --which anymal   # Isaac-Velocity-Flat-Anymal-D-v0 -> anymal_d_flat_third_person.png
```

## Files

- `main.py` - Modal image and entrypoint
- `smoke.py` - `run_smoke(task, out, eye, target)`: runs inside the container
