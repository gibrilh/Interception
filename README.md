# Drone Interceptor

## Why this exists

I saw a LinkedIn post of someone running a 2D simulation of a missile intercepting a target, and I wanted to turn it into something you can pilot in basic 3D. This project is that: a drone-interception sim where you fly a drone under proportional-navigation missile guidance and try to reach a goal zone before you get hit.

Mostly this was a way to get comfortable with a real coding project before starting my masters - picking something with physics, geometry, and a bit of controls theory in it felt like a good bridge between my mechanical engineering background and the Applied Computational Science and Engineering degree I'm starting at Imperial. It also doubled as my first proper attempt at using Git and GitHub as an actual workflow rather than just a place to dump code.

This is a finished prototype, not a finished game. Things I want to add next: better graphics, buildings to weave between, multiple interceptors at once, and a more complete HUD. I'll keep building on it during the year

## How to play

You control a drone with keyboard input, and your job is to reach the green goal zone before the interceptor missile catches you. The missile only launches once you fly the drone inside the launch site's red detection dome - stay outside it and nothing chases you, but you also can't reach most goals without eventually passing near a launch site.

**Controls:**

| Key | Action |
| --- | --- |
| `W` / `S` | Forward / backward |
| `A` / `D` | Strafe left / right |
| `Space` | Ascend |
| `Left Shift` | Descend |
| `C` | Toggle camera mode |
| `+` / `-` | Zoom (fixed camera only) |
| Arrow keys | Look around (FPV camera only) |
| Mouse click | Restart after game over |

**The two cameras:**

- **Fixed/orbit camera** (default): a locked-off overview angle looking down at the whole play area, so you can see the drone, the missile, and the goal at the same time. WASD always moves the drone the same way regardless of where you're looking, since the camera doesn't rotate. Zoom in/out with `+`/`-`.
- **FPV camera**: a chase camera right behind the drone, looking where the drone is heading. You can look around freely with the arrow keys. This is the more immersive, harder-to-fly view - fog kicks in here to keep visibility feeling tight and cockpit-like. Toggle between the two with `C`.

**How to actually win:** once the missile is locked on, don't just fly straight for the goal, it will mostly get to you before. The missile uses proportional navigation, which is good at closing distance smoothly but reacts to how fast your relative position is sweeping across its sight line. If you jink, suddenly reverse or cut sideways, especially once the missile is close, you spike that sweep rate and force it into a hard, often overcorrected turn. Time your jinks right and the missile overshoots or has to burn distance recovering, buying you the opening to get to the goal.

## Code overview

- **[main.py](main.py)** - the game loop. Reads input, updates the drone and missile each frame, checks win/loss conditions, and draws everything including the HUD.
- **[drone.py](drone.py)** - the player-controlled drone: acceleration/braking physics (tuned to rough DJI Air 3S values, see below) and its visual facing direction.
- **[interceptor.py](interceptor.py)** - the missile, its launch site, and the goal zone. This is where the proportional navigation guidance lives.
- **[camera.py](camera.py)** - the two camera modes (fixed overview and FPV) and the one-time OpenGL setup.
- **[rendering.py](rendering.py)** - shared drawing code: the drone/missile shape, trails, ground grid, and all HUD elements (speed, altitude, compass, timer, goal distance).
- **[constants.py](constants.py)** - shared tunable values (arena size, speed caps, detection/goal radii), grouped by which files actually use them.

## Proportional navigation, and how it's used here

Proportional navigation (PN) is the guidance law real heat-seeking and radar-guided missiles use. Instead of just steering straight at wherever the target currently is (which lags behind and produces a big curve), PN watches how fast the line of sight to the target is rotating and steers to cancel that rotation out. A line of sight that isn't rotating at all means the missile and target are on a collision course, so it goes for it. 

In `interceptor.py`, `Interceptor.update()` does this every frame:

1. **Line of sight and its rotation rate.** `omega = cross(R, V_rel) / range²` - the vector from missile to target crossed with the relative velocity, scaled by range squared, gives the angular rate the sight-line is sweeping at.
2. **Closing velocity.** `Vc = -dot(V_rel, los_unit)` - how fast the distance between missile and target is actually shrinking. If the target is pulling away faster than the missile is gaining, true PN math breaks down, so the missile falls back to just pointing straight at the target instead.
3. **Steering direction.** `cross(omega, los_unit)` gives the direction that reduces the sight-line's rotation rate - this is the actual PN steering command.
4. **Turn-rate-limited heading update.** The missile rotates its heading toward that steering direction, but capped at a maximum turn rate (its "how sharp can it bank" limit) rather than an unlimited acceleration, so it behaves like something with a real airframe rather than an omniscient homing dot.
5. **Rebuild velocity from heading**, with separate horizontal and vertical speed caps, mirroring how the drone itself moves.

There's also a low-pass filter on `omega` (`omega_smoothed`) so the missile doesn't violently snap its aim on every single frame of jinking - it blends the new reading in gradually instead of reacting instantly, which is closer to how a real seeker head behaves and is exactly why jinking near the missile still works as a tactic rather than being an exploit: overreacting to a spiking sight-line rate is a genuine, well-known weakness of PN, not a bug.

---

# DJI Air 3S Movement Values

DJI publishes max speeds for the Air 3S but not acceleration or braking figures, so these are estimates used to give the drone a plausible, controlled feel rather than an arcade-y one.

| Axis | Max speed | Accelerate | Release (coast to stop) | Brake (opposite key) |
| --- | ---: | ---: | ---: | ---: |
| Horizontal (x/z) | `21.0 m/s` | `4.5 m/s²` | `5.5 m/s²` | `7.0 m/s²` |
| Vertical up | `10.0 m/s` | `3.5 m/s²` | `5.0 m/s²` | `5.0 m/s²` |
| Vertical down | `10.0 m/s` | `4.0 m/s²` | `5.0 m/s²` | `5.0 m/s²` |

Each axis has three separate rates, because the drone should react differently depending on player intent:

- **Accelerate** - held input, same direction as current velocity (or starting from rest): speeds up toward max.
- **Release** - no input: coasts down to a stop, like a flight controller holding position rather than drifting.
- **Brake** - opposite input pressed while still moving the old way: kills the existing velocity first, faster than either of the above. Once speed hits zero, it switches to normal acceleration in the new direction - a reversal is always brake-to-zero, then accelerate, never an instant flip.

Braking is the fastest of the three because stopping matters more than reaching top speed quickly, and pressing the opposite key is a stronger signal of intent than just releasing - the drone should feel tight and controlled rather than loose. Horizontal axes (forward/back, left/right) are handled independently, so a diagonal input decelerates one axis while accelerating the other at the same time, giving a curved transition instead of a stop-then-go.
