# Structure of the code 

drone interception sim:
    main.py
    drone.py
    rendering.py
    camera.py
    constants.py




# DJI Air 3S Movement Values for the Simulation

These values are estimates for the simulation. DJI gives maximum speed values for the Air 3S, but it does not provide official acceleration or braking values.

## Main Values

### Horizontal Movement

| Value                                   |     Amount |
| --------------------------------------- | ---------: |
| Maximum horizontal speed                | `21.0 m/s` |
| Horizontal acceleration                 | `4.5 m/s²` |
| Deceleration after releasing the key    | `5.5 m/s²` |
| Braking after pressing the opposite key | `7.0 m/s²` |

These values are used for forward, backward, left, and right movement.

### Vertical Movement

| Value                             |     Amount |
| --------------------------------- | ---------: |
| Maximum upward speed              | `10.0 m/s` |
| Maximum downward speed            | `10.0 m/s` |
| Upward acceleration               | `3.5 m/s²` |
| Downward acceleration             | `4.0 m/s²` |
| Vertical deceleration and braking | `5.0 m/s²` |

## The Three Types of Speed Change

The simulation uses three different rates:

1. Acceleration
2. Deceleration after releasing the input
3. Braking after pressing the opposite input

These are separate because the drone should react differently depending on what the player is doing.

## Normal Acceleration

Normal acceleration is used when the drone is gaining speed in the same direction as the current input.

This happens when:

* The drone is stopped and a direction is pressed.
* The drone is already moving in that direction.
* The drone has not yet reached its maximum speed.

For horizontal movement, the acceleration is:

```text
4.5 m/s²
```

For example, if the drone starts from rest and moves right, the speed would increase like this at one-second intervals:

```text
0.0 m/s
4.5 m/s
9.0 m/s
13.5 m/s
18.0 m/s
21.0 m/s
```

The speed stops increasing when it reaches the maximum horizontal speed of `21.0 m/s`.

The exact values between frames depend on the simulation timestep, but the general behavior stays the same.

## Deceleration After Releasing the Key

When the player releases a movement key, the target speed becomes zero.

The drone does not keep drifting freely. A DJI drone uses its flight controller to slow down and hold its position.

For horizontal movement, the release deceleration is:

```text
5.5 m/s²
```

For example, if the drone is moving right at `11.0 m/s` and the key is released:

```text
11.0 m/s
5.5 m/s
0.0 m/s
```

This means releasing the key causes the drone to stop faster than it normally accelerates.

However, it stops more slowly than when the player presses the opposite direction.

## Braking After Pressing the Opposite Key

Opposite-input braking happens when the drone is moving in one direction and the player presses the opposite direction.

For example:

```text
Current movement: right
Current speed: 10.0 m/s
New input: left
```

This movement is split into two parts.

### First Part: Braking

The drone first removes its existing rightward speed.

The braking rate is:

```text
7.0 m/s²
```

The speed moves toward zero:

```text
10.0 m/s right
3.0 m/s right
0.0 m/s
```

The exact values depend on the timestep, but the important part is that the speed is reduced at `7.0 m/s²`.

### Second Part: Accelerating in the New Direction

Once the drone reaches zero speed, the braking phase ends.

It then starts accelerating left using the normal horizontal acceleration:

```text
4.5 m/s²
```

The full movement is:

```text
Moving right
Brake at 7.0 m/s²
Reach 0.0 m/s
Accelerate left at 4.5 m/s²
```

The `7.0 m/s²` value is only used to remove the old velocity.

It is not used to accelerate in the new direction.

## Why Braking Is Faster Than Acceleration

The three horizontal rates are:

| Behavior                     |       Rate |
| ---------------------------- | ---------: |
| Normal acceleration          | `4.5 m/s²` |
| Deceleration after release   | `5.5 m/s²` |
| Braking after opposite input | `7.0 m/s²` |

Braking is faster than acceleration because stopping is usually more important than reaching full speed quickly.

A DJI drone is designed to feel controlled and stable. When the pilot releases the controls, the drone should slow down and hold position instead of drifting for a long time.

Pressing the opposite direction also shows a stronger intention than simply releasing the controls.

Releasing the key means:

```text
Stop moving.
```

Pressing the opposite key means:

```text
Stop moving in the current direction, then move the other way.
```

Because of that, opposite-input braking uses the strongest rate.

Using a lower acceleration and stronger braking also makes the drone feel less loose in the simulation.

## Horizontal Movement Patterns

### Starting From Rest

If the drone is stopped and the player presses right:

```text
Current speed: 0.0 m/s
Input: right
Target speed: 21.0 m/s right
Acceleration: 4.5 m/s²
```

The drone accelerates right until it reaches maximum speed.

### Continuing in the Same Direction

If the drone is already moving right at `10.0 m/s` and the player continues holding right:

```text
Current speed: 10.0 m/s right
Input: right
Target speed: 21.0 m/s right
Acceleration: 4.5 m/s²
```

The drone continues gaining speed until it reaches `21.0 m/s`.

### Releasing the Input

If the drone is moving right at `10.0 m/s` and the player releases the key:

```text
Current speed: 10.0 m/s right
Input: none
Target speed: 0.0 m/s
Deceleration: 5.5 m/s²
```

The drone slows down until it stops.

### Pressing the Opposite Direction

If the drone is moving right at `10.0 m/s` and the player presses left:

```text
Current speed: 10.0 m/s right
Input: left
```

The behavior is:

```text
Brake from 10.0 m/s right to 0.0 m/s
Braking rate: 7.0 m/s²

Then accelerate from 0.0 m/s toward the left
Acceleration rate: 4.5 m/s²
```

### Releasing the Key During a Reversal

Suppose the drone is moving right and the player presses left.

The drone starts braking toward zero.

If the player releases the left key before the drone reaches zero, the target becomes zero instead of leftward movement.

For example:

```text
Current speed: 3.0 m/s right
Input: none
Target speed: 0.0 m/s
Deceleration: 5.5 m/s²
```

The drone finishes stopping.

It does not continue into leftward movement because the left input is no longer being held.

### Changing to a Perpendicular Direction

Suppose the drone is moving right and the player presses forward.

The right-left axis and the forward-backward axis are handled separately.

The rightward speed begins moving toward zero while the forward speed begins increasing.

This means the drone changes direction in a curve instead of stopping completely before moving forward.

For example:

```text
Rightward velocity: decelerates toward 0
Forward velocity: accelerates toward maximum forward speed
```

Both changes can happen at the same time.

## Vertical Movement Patterns

### Moving Up

When the player presses up:

```text
Maximum upward speed: 10.0 m/s
Upward acceleration: 3.5 m/s²
```

The drone accelerates upward until it reaches the maximum upward speed.

### Moving Down

When the player presses down:

```text
Maximum downward speed: 10.0 m/s
Downward acceleration: 4.0 m/s²
```

The drone accelerates downward until it reaches the maximum downward speed.

### Releasing Vertical Input

When the player releases the vertical input:

```text
Target vertical speed: 0.0 m/s
Vertical deceleration: 5.0 m/s²
```

The drone stops climbing or descending and then holds its altitude.

### Reversing From Up to Down

If the drone is moving upward and the player presses down:

```text
Remove upward speed at 5.0 m/s²
Reach 0.0 m/s
Accelerate downward at 4.0 m/s²
```

The drone does not instantly switch from moving up to moving down.

It must first remove the upward velocity.

### Reversing From Down to Up

If the drone is moving downward and the player presses up:

```text
Remove downward speed at 5.0 m/s²
Reach 0.0 m/s
Accelerate upward at 3.5 m/s²
```

Again, the drone first stops its current movement before gaining speed in the new direction.

## Summary of Behavior

| Current State              | Input                           | Result                                             |
| -------------------------- | ------------------------------- | -------------------------------------------------- |
| Stopped                    | Direction pressed               | Accelerate in that direction                       |
| Moving below maximum speed | Same direction held             | Continue accelerating                              |
| At maximum speed           | Same direction held             | Maintain maximum speed                             |
| Moving                     | Input released                  | Decelerate toward zero                             |
| Moving                     | Opposite direction pressed      | Brake toward zero                                  |
| Speed reaches zero         | Opposite direction still held   | Accelerate in the new direction                    |
| Moving horizontally        | Perpendicular direction pressed | Decelerate on one axis and accelerate on the other |
| Moving vertically          | Vertical input released         | Stop vertical movement and hold altitude           |

## Main Rule

Braking removes the current velocity.

Acceleration creates velocity in the new direction.

For a horizontal reversal:

```text
Brake at 7.0 m/s² until the speed reaches zero.
Then accelerate at 4.5 m/s² in the new direction.
```

For released horizontal input:

```text
Decelerate at 5.5 m/s² until the speed reaches zero.
```

For vertical movement:

```text
Decelerate or brake at 5.0 m/s² until vertical speed reaches zero.
Then use either 3.5 m/s² upward acceleration
or 4.0 m/s² downward acceleration.
```
