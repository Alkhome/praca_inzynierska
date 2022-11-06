nose = [landmarks[self.mp_pose.PoseLandmark.NOSE.value].x,
        landmarks[self.mp_pose.PoseLandmark.NOSE.value].y]
right_eye_inner = [landmarks[self.mp_pose.PoseLandmark.LEFT_EYE_INNER.value].x,
                   landmarks[self.mp_pose.PoseLandmark.LEFT_EYE_INNER.value].y]
right_eye = [landmarks[self.mp_pose.PoseLandmark.LEFT_EYE.value].x,
             landmarks[self.mp_pose.PoseLandmark.LEFT_EYE.value].y]
right_eye_outer = [landmarks[self.mp_pose.PoseLandmark.LEFT_EYE_OUTER.value].x,
                   landmarks[self.mp_pose.PoseLandmark.LEFT_EYE_OUTER.value].y]

left_eye_inner = [landmarks[self.mp_pose.PoseLandmark.RIGHT_EYE_INNER.value].x,
                  landmarks[self.mp_pose.PoseLandmark.RIGHT_EYE_INNER.value].y]
left_eye = [landmarks[self.mp_pose.PoseLandmark.RIGHT_EYE.value].x,
            landmarks[self.mp_pose.PoseLandmark.RIGHT_EYE.value].y]
left_eye_outer = [landmarks[self.mp_pose.PoseLandmark.RIGHT_EYE_OUTER.value].x,
                  landmarks[self.mp_pose.PoseLandmark.RIGHT_EYE_OUTER.value].y]

right_ear = [landmarks[self.mp_pose.PoseLandmark.LEFT_EAR.value].x,
             landmarks[self.mp_pose.PoseLandmark.LEFT_EAR.value].y]
left_ear = [landmarks[self.mp_pose.PoseLandmark.RIGHT_EAR.value].x,
            landmarks[self.mp_pose.PoseLandmark.RIGHT_EAR.value].y]

right_mouth = [landmarks[self.mp_pose.PoseLandmark.MOUTH_LEFT.value].x,
               landmarks[self.mp_pose.PoseLandmark.MOUTH_LEFT.value].y]
left_mouth = [landmarks[self.mp_pose.PoseLandmark.MOUTH_RIGHT.value].x,
              landmarks[self.mp_pose.PoseLandmark.MOUTH_RIGHT.value].y]

right_shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                  landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
left_shoulder = [landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                 landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]

right_elbow = [landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
               landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
left_elbow = [landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
              landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]

right_wrist = [landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x,
               landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y]
left_wrist = [landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
              landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

right_pinky = [landmarks[self.mp_pose.PoseLandmark.LEFT_PINKY.value].x,
               landmarks[self.mp_pose.PoseLandmark.LEFT_PINKY.value].y]
left_pinky = [landmarks[self.mp_pose.PoseLandmark.RIGHT_PINKY.value].x,
              landmarks[self.mp_pose.PoseLandmark.RIGHT_PINKY.value].y]
right_index = [landmarks[self.mp_pose.PoseLandmark.LEFT_INDEX.value].x,
               landmarks[self.mp_pose.PoseLandmark.LEFT_INDEX.value].y]
left_index = [landmarks[self.mp_pose.PoseLandmark.RIGHT_INDEX.value].x,
              landmarks[self.mp_pose.PoseLandmark.RIGHT_INDEX.value].y]
right_thumb = [landmarks[self.mp_pose.PoseLandmark.LEFT_THUMB.value].x,
               landmarks[self.mp_pose.PoseLandmark.LEFT_THUMB.value].y]
left_thumb = [landmarks[self.mp_pose.PoseLandmark.RIGHT_THUMB.value].x,
              landmarks[self.mp_pose.PoseLandmark.RIGHT_THUMB.value].y]

left_hip = [landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].x,
             landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y]
right_hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
             landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]

left_knee = [landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
             landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
right_knee = [landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x,
             landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y]
