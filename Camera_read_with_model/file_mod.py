def save_to_file(values):
    try:
        calibration_file = open("miscellaneous/exercises_params.txt", "w")
        for param in values:
            calibration_file.write(str(param) + "\n")
        calibration_file.close()
    except:
        print("Error occured while trying to save values")


if __name__ == "__main__":
    pass
