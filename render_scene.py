# python3 main.py /Users/jason/tmp/model-viewer/packages/shared-assets/models/glTF-Sample-Models/2.0/Fox/glTF/Fox.gltf --output_file /Users/jason/tmp/model-viewer/packages/render-fidelity-tools/test/goldens/khronos-Fox/vray-golden.png --render_mode production --default_cam_rot '(-60,0,0)' --default_cam_look_at '(-35,37,25)' --default_cam_pos '(0,0,124)' --size '(1536,1536)' --num_frames 1
import bpy
import json
import numpy as np
import math
import os
from mathutils import Vector

os.system("cls")

# bpy.ops.wm.read_factory_settings(use_empty=True)


def reset_blend():
    # Remove all objects in the current scene
    scene = bpy.context.scene
    for obj in scene.objects:
        bpy.data.objects.remove(obj)

    bpy.ops.outliner.orphans_purge(
        do_local_ids=True, do_linked_ids=True, do_recursive=True
    )


reset_blend()


# Now you can work with the 'data' variable
# print(data)


# https://docs.blender.org/api/current/bpy.ops.import_scene.html#bpy.ops.import_scene.gltf

EXAMPLE_ARG = {
    "scenario": {
        "lighting": "../../../shared-assets/environments/lightroom_14b.hdr",
        "dimensions": {"width": 1536, "height": 900},
        "target": {"x": 0, "y": 0.3, "z": 0},
        "orbit": {"theta": 0, "phi": 90, "radius": 1},
        "verticalFoV": 45,
        "renderSkybox": False,
        "name": "khronos-SheenChair",
        "model": "../../../shared-assets/models/glTF-Sample-Models/2.0/SheenChair/glTF-Binary/SheenChair.glb",
    },
    "outputFile": "../../../test/goldens/khronos-SheenChair/stellar-golden.png",
}

# EXAMPLE_ARG = {
#     "scenario": {
#         "name": "khronos-IridescentDishWithOlives",
#         "model": "../../../shared-assets/models/glTF-Sample-Models/2.0/IridescentDishWithOlives/glTF-Binary/IridescentDishWithOlives.glb",
#         "lighting": "../../../shared-assets/environments/spruit_sunrise_1k_HDR.hdr",
#         "renderSkybox": True,
#         "orbit": {"radius": 0.47, "theta": -70},
#         "dimensions": {"height": 570},
#         "verticalFoV": 45,
#         "target": {"y": 0.11},
#         "exclude": ["babylon"],
#         "dimensions": {"width": 1356, "height": 900},
#     },
#     "outputFile": "../../../test/goldens/khronos-SheenChair/stellar-golden.png",
# }


json_file_path = "F:/net/blender_python_render/tasks.json"

root_folder = "F:/net/blender_python_render/"


def convert_target(original_target):
    # Create a new target dictionary with default values
    new_target = {"x": 0, "y": 0, "z": 0}

    # Update the new_target dictionary with values from the original_target
    for key in original_target:
        new_target[key] = original_target[key]

    return new_target


def bounding_sphere(objects, mode="BBOX"):
    # return the bounding sphere center and radius for objects (in global coordinates)
    if not isinstance(objects, list):
        objects = [objects]
    points_co_global = []
    if mode == "GEOMETRY":
        # GEOMETRY - by all vertices/points - more precis, more slow
        for obj in objects:
            points_co_global.extend(
                [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
            )
    elif mode == "BBOX":
        # BBOX - by object bounding boxes - less precis, quick
        for obj in objects:
            points_co_global.extend(
                [obj.matrix_world @ Vector(bbox) for bbox in obj.bound_box]
            )

    def get_center(l):
        return (max(l) + min(l)) / 2 if l else 0.0

    x, y, z = [[point_co[i] for point_co in points_co_global] for i in range(3)]
    b_sphere_center = (
        Vector([get_center(axis) for axis in [x, y, z]]) if (x and y and z) else None
    )
    b_sphere_radius = (
        max(((point - b_sphere_center) for point in points_co_global))
        if b_sphere_center
        else None
    )
    return b_sphere_center, b_sphere_radius.length


def main(scenario):
    name = scenario.get("name", "noName")
    print("name: ", name)
    # config = json.loads(sys.argv[1])

    # scenario = config["scenario"]
    outpath = ""  # config["outputFile"]

    # parse scenario
    resolution = [1536, 1536]
    if scenario.get("dimensions"):
        resolution[0] = scenario["dimensions"].get("width", resolution[0])
        resolution[1] = scenario["dimensions"].get("height", resolution[1])

    scenePath = "shared-assets" + scenario["model"].split("shared-assets")[1]

    iblPath = "shared-assets/environments/lightroom_14b.hdr"

    if scenario.get("lighting"):
        iblPath = "shared-assets" + scenario["lighting"].split("shared-assets")[1]

    renderSkybox = False
    if scenario.get("renderSkybox"):
        renderSkybox = scenario["renderSkybox"]

    # target = np.array(
    #     [scenario["target"]["x"], scenario["target"]["y"], scenario["target"]["z"]]
    # )
    target = {"x": 0, "y": 0, "z": 0}
    if scenario.get("target"):
        target = convert_target(scenario["target"])
    print("target:", target)
    theta = 0
    phi = 90
    radius = 1
    if scenario.get("orbit"):
        theta = scenario["orbit"].get("theta", theta)
        phi = scenario["orbit"].get("phi", phi)
        radius = scenario["orbit"].get("radius", radius)

    verticalFov = 45
    if scenario.get("verticalFoV"):
        verticalFov = scenario["verticalFoV"]
    aspect = resolution[0] / resolution[1]

    GLTF_PATH = root_folder + scenePath
    HDRI_PATH = root_folder + iblPath
    RENDER_PATH = "F:/net/blender_python_render/output/"
    print("outpath:", outpath)
    print("resolution:", resolution)
    print("scenePath:", scenePath)
    print("gltf full path:", GLTF_PATH)

    print("iblPath:", iblPath)
    print("renderSkybox:", renderSkybox)
    print("target:", target)
    print("theta:", theta)
    print("phi:", phi)
    print("radius:", radius)
    print("verticalFov:", verticalFov)
    print("aspect:", aspect)

    bpy.context.scene.render.resolution_x = resolution[0]
    bpy.context.scene.render.resolution_y = resolution[1]

    # Import the GLTF model
    bpy.ops.import_scene.gltf(filepath=GLTF_PATH)

    bpy.ops.object.empty_add(
        type="SINGLE_ARROW", align="WORLD", location=(0, 0, 0), scale=(1, 1, 1)
    )
    targetObj = bpy.context.object
    targetObj.name = "target"

    # Add a camera
    bpy.ops.object.camera_add(
        enter_editmode=False,
        align="VIEW",
        location=(0, 0, radius),
        rotation=(0, 0, 0),
        scale=(1, 1, 1),
    )
    camera = bpy.context.object
    camera.data.lens_unit = "FOV"
    camera.data.lens = verticalFov  # vertical_fov_to_horizontal(verticalFov, aspect)
    bpy.context.scene.camera = camera

    # Calculate the horizontal FOV from the vertical FOV and aspect ratio
    horizontalFov = 2 * np.arctan(np.tan(np.radians(verticalFov) / 2) * aspect)

    # Set the camera's field of view
    camera.data.angle = horizontalFov

    # Set the empty as the parent of the camera
    targetObj.select_set(True)
    camera.select_set(True)

    bpy.context.view_layer.objects.active = targetObj

    bpy.ops.object.parent_set(
        type="OBJECT",
        keep_transform=False,
    )

    targetObj.location.x = target["x"]
    targetObj.location.y = target["z"]
    targetObj.location.z = target["y"]

    targetObj.rotation_euler[0] = math.radians(phi)
    targetObj.rotation_euler[1] = 0
    targetObj.rotation_euler[2] = math.radians(theta)

    meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    b_sphere_co, b_sphere_radius = bounding_sphere(objects=meshes, mode="GEOMETRY")

    radius = max(radius, b_sphere_radius, 1e-5)
    camera.data.clip_start = 2 * radius / 1000
    camera.data.clip_end = 2 * radius

    print(b_sphere_co, b_sphere_radius)

    # Set up HDRI lighting and background color
    scn = bpy.context.scene
    if not scn.world:
        bpy.ops.world.new()

    scn.world.use_nodes = True
    wd = scn.world
    ntree = bpy.data.worlds[wd.name].node_tree
    # clear existing nodes
    for node in ntree.nodes:
        ntree.nodes.remove(node)

    hdriNode = ntree.nodes.new(type="ShaderNodeTexEnvironment")
    hdriNode.location = 0, 0
    hdriNode.image = bpy.data.images.load(HDRI_PATH)

    defNode = ntree.nodes.new("ShaderNodeBackground")
    defNode.location = 250, 0

    outputNode = ntree.nodes.new("ShaderNodeOutputWorld")
    outputNode.location = 500, 0

    ntree.links.new(hdriNode.outputs[0], defNode.inputs[0])
    ntree.links.new(defNode.outputs[0], outputNode.inputs[0])

    bpy.context.scene.render.film_transparent = not renderSkybox
    # bpy.context.scene.render.engine = "BLENDER_EEVEE"
    bpy.context.scene.render.engine = "CYCLES"
    bpy.context.scene.cycles.device = "GPU"
    bpy.context.scene.cycles.samples = 4096
    bpy.context.scene.cycles.use_denoising = True
    bpy.context.scene.cycles.time_limit = 20

    # bpy.context.scene.render.image_settings.file_format = "JPEG"
    # bpy.context.scene.render.image_settings.quality = 90
    # bpy.context.scene.render.image_settings.color_mode = "RGB"

    bpy.context.scene.view_settings.view_transform = "AgX"
    bpy.context.scene.render.image_settings.file_format = "PNG"
    bpy.context.scene.render.image_settings.color_mode = "RGBA"
    bpy.context.scene.render.image_settings.compression = 15

    bpy.context.scene.render.filepath = RENDER_PATH + "cycles_" + name

    bpy.ops.render.render(write_still=True)


# setup scene
# scene = load_scene(scenePath)
# camera = create_camera(scene, target, verticalFov, aspect, theta, phi, radius)
# ibl = create_hdri_light(scene, iblPath, renderSkybox)


# print(camera.location)
# Open the JSON file for reading
with open("F:/net/blender_python_render/config.json", "r") as file:
    data = json.load(file)
    all_scenarios = data["scenarios"]
    scenario = all_scenarios[9]
    main(scenario)
