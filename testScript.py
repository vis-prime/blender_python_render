import json
import subprocess
import os
from PIL import Image
import shutil


os.system("cls")

# Load the JSON data from the file
with open("F:/net/blender_python_render/config.json", "r") as file:
    data = json.load(file)

# Get the desired scenario (for example, the 9th scenario)

total = len(data["scenarios"])
for i, scenario in enumerate(data["scenarios"]):
    print(i, "/", total, scenario["name"])

    # if i == 80:
    #     break

    dummyData = {
        "scenario": scenario,
        # "outputFile": "F:/net/blender_python_render/output/goldens/"
        # + scenario["name"]
        # + "/cycles-golden.png",
        # directly in output
        "outputFile": "F:/net/blender_python_render/output/"
        + scenario["name"]
        + "_cycles.png",
    }

    # get proper resolution
    image_path = (
        "F:/net/blender_python_render/output/goldens/"
        + scenario["name"]
        + "/three-gpu-pathtracer-golden.png"
    )
    if os.path.exists(image_path):
        with Image.open(image_path) as img:
            width, height = img.size
            if not scenario.get("dimensions"):
                scenario["dimensions"] = {}
            scenario["dimensions"]["width"] = width
            scenario["dimensions"]["height"] = height
            print("new resolution", width, height)

    model_viewer_image = (
        "F:/net/blender_python_render/output/goldens/"
        + scenario["name"]
        + "/model-viewer-golden.png"
    )

    if os.path.exists(model_viewer_image):
        new_name = scenario["name"] + "_model-viewer.png"
        output_dir = "F:/net/blender_python_render/output/"

        # Construct the new path with the new name
        new_path = os.path.join(output_dir, new_name)

        # Copy the image to the new path
        shutil.copy(model_viewer_image, new_path)

    print(dummyData["outputFile"])

    if os.path.exists(dummyData["outputFile"]):
        print("file exists\n\n")
        continue

    if not scenario.get("model"):
        print("no file\n\n")
        continue

    # Convert the scenario to a JSON string
    dummy_json = json.dumps(dummyData)

    print("NAME:", scenario["name"])

    # Run the render_scene.py script with the scenario JSON as an argument
    subprocess.run(
        [
            "C:/b3d beta/blender.exe",
            "-b",
            "-P",
            "F:/net/blender_python_render/render_scene.py",
            "--",
            dummy_json,
        ]
    )
