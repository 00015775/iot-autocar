# Components Logic

## Combining the L298N+IR+Ultra code so the system works as a single program:

1. IR sensors (_mounted near the ground_) continuously check for obstacles at ground level.
2. Ultrasonic sensor (_mounted on a servo motor_) continuously checks the distance in the forward direction.
3. When either
  * the IR sensors detect an obstacle, or
  * the ultrasonic sensor detects an object closer than a defined threshold,
  * the car **must stop immediately**.
4. When the car has stopped, the servo motor begins a full 180° scan to search for the clearest path:
  * The servo starts at its neutral position (90°).
  * It sweeps from 90° → 0°, then 0° → 180°, and finally returns 180° → 90°.
  * The ultrasonic sensor measures the distance at each angle.
  * While sweeping back and forth, some angles are scanned twice (e.g., 90°→0° and 0°→90°).
  * Duplicate readings are avoided and only one value for each angle is kept.
5. After the sweep, the program compares all stored distances and chooses the angle with the largest distance as the direction to move towards.
6. The servo then returns to its initial 90° position, but the ultrasonic sensor continues monitoring the front direction during driving.
7. Before moving toward the chosen direction, the car should reverse slightly to create space between itself and the detected obstacle standing in the front.
8. After reversing, the car rotates/moves toward the selected direction and continues driving normally.
9. This behavior repeats:
  * The servo only performs a sweep when an obstacle is detected by either the IR sensors or the ultrasonic sensor.
  * Otherwise, the car continues driving straight with continuous distance monitoring.

