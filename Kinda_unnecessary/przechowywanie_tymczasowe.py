self.left_arm_bend_calibration_results.append(int(angle))

if keyboard.is_pressed('space'):
    time.sleep(2)
    print(self.calculate_mean(self.left_arm_bend_calibration_results, reversed=True))
    self.current_exercise_name = EXERCISES[1]

if len(self.left_arm_bend_calibration_results) > 50:
    self.left_arm_bend_calibration_results.sort(reverse=True)
    self.left_arm_bend_calibration_results = self.left_arm_bend_calibration_results[30:]