import json
import subprocess
import os
from PIL import Image
import shutil


# os.system("cls")

# Load the JSON data from the file
with open("F:/net/blender_python_render/config.json", "r") as file:
    data = json.load(file)

# Get the desired scenario (for example, the 9th scenario)
root_folder = "F:/net/blender_python_render/"

total = len(data["scenarios"])
for i, scenario in enumerate(data["scenarios"]):
    print(i, "/", total, scenario["name"])

    if i == 1:
        break

    dummyData = {
        "scenario": {
            "lighting": "F:/net/blender_python_render/shared-assets/environments/lightroom_14b.hdr",
            "dimensions": {"width": 768, "height": 450},
            "target": {"x": 0, "y": 0, "z": 0},
            "orbit": {"theta": 0, "phi": 90, "radius": 1},
            "verticalFoV": 45,
            "renderSkybox": False,
            "name": "khronos-SheenChair",
            "model": "../../../shared-assets/models/glTF-Sample-Models/2.0/SheenChair/glTF-Binary/SheenChair.glb",
        },
        "outputFile": "F:/net/blender_python_render/output/"
        + scenario["name"]
        + "_cycles.png",
    }

    if os.path.exists(dummyData["outputFile"]):
        print("already done", scenario["name"])
        continue

    dummyScenario = dummyData["scenario"]

    for key in scenario:
        # Check if the key has subkeys
        if isinstance(scenario[key], dict):
            for sub_key in scenario[key]:
                dummyScenario[key][sub_key] = scenario[key].get(
                    sub_key, dummyScenario[key].get(sub_key)
                )
        else:
            dummyScenario[key] = scenario[key]

    dummyScenario["model"] = (
        root_folder + "shared-assets" + scenario["model"].split("shared-assets")[1]
    )

    # dimensions
    image_path = (
        "F:/net/blender_python_render/output/goldens/"
        + scenario["name"]
        + "/three-gpu-pathtracer-golden.png"
    )

    if os.path.exists(image_path):
        with Image.open(image_path) as img:
            width, height = img.size
            dummyScenario["dimensions"]["width"] = width
            dummyScenario["dimensions"]["height"] = height

    # IBL
    if scenario.get("lighting"):
        iblPath = (
            root_folder
            + "shared-assets"
            + scenario["lighting"].split("shared-assets")[1]
        )
    # outpath
    three_gpu_pathtracer_image = (
        "F:/net/blender_python_render/output/goldens/"
        + scenario["name"]
        + "/three-gpu-pathtracer-golden.png"
    )

    compare_image_path = ""
    if os.path.exists(three_gpu_pathtracer_image):
        compare_image_path = three_gpu_pathtracer_image
    else:
        compare_image_path = (
            "F:/net/blender_python_render/output/goldens/"
            + scenario["name"]
            + "/model-viewer-golden.png"
        )

    new_name = scenario["name"] + "_compare.png"
    output_dir = "F:/net/blender_python_render/output/"

    # Construct the new path with the new name
    new_path = os.path.join(output_dir, new_name)

    # Copy the image to the new path
    shutil.copy(compare_image_path, new_path)

    if not scenario.get("model"):
        print("no file/n/n")
        continue

    # Convert the scenario to a JSON string
    dummy_json = json.dumps(dummyData)

    pretty_dummy_scenario = json.dumps(dummyScenario, indent=4)
    print(pretty_dummy_scenario)
    commands = [
        "C:/b3d beta/blender.exe",
        "-b",
        "-P",
        "F:/net/model-viewer/packages/render-fidelity-tools/test/renderers/blender-cycles/render.py",
        "--",
        dummy_json,
    ]

    commandStr = ''

    for cmd in commands:
        commandStr += cmd + ' '
    # print('\n\n\n')
    # print(commandStr)

    # Run the render_scene.py script with the scenario JSON as an argument
    subprocess.run(commands)
