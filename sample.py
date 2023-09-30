def main():
    """cmd render script

    ARGS:
        argv[1] (str): The stringified json object containing scenario config and outputPath properties
        Example:
        {
          "scenario": {
            "lighting": "../../../shared-assets/environments/lightroom_14b.hdr",
            "dimensions": {
              "width": 768,
              "height": 450
            },
            "target": {
              "x": 0,
              "y": 0.3,
              "z": 0
            },
            "orbit": {
              "theta": 0,
              "phi": 90,
              "radius": 1
            },
            "verticalFoV": 45,
            "renderSkybox": False,
            "name": "khronos-SheenChair",
            "model": "../../../shared-assets/models/glTF-Sample-Models/2.0/SheenChair/glTF-Binary/SheenChair.glb"
          },
          "outputFile": "../../../test/goldens/khronos-SheenChair/stellar-golden.png"
        }
    """
    config = json.loads(sys.argv[1])

    scenario = config["scenario"]
    outpath = config["outputFile"]

    # parse scenario
    resolution = (scenario["dimensions"]["width"], scenario["dimensions"]["height"])
    scenePath = "shared-assets" + scenario["model"].split("shared-assets")[1]
    iblPath = "shared-assets" + scenario["lighting"].split("shared-assets")[1]
    renderSkybox = scenario["renderSkybox"]

    target = np.array(
        [scenario["target"]["x"], scenario["target"]["y"], scenario["target"]["z"]]
    )
    theta = scenario["orbit"]["theta"]
    phi = scenario["orbit"]["phi"]
    radius = scenario["orbit"]["radius"]
    verticalFov = scenario["verticalFoV"]
    aspect = resolution[0] / resolution[1]

    # setup scene
    scene = load_scene(scenePath)
    camera = create_camera(scene, target, verticalFov, aspect, theta, phi, radius)
    ibl = create_hdri_light(scene, iblPath, renderSkybox)

    # render
    beauty_image = render_scene(config, scene, renderer, camera, ibl, NUM_SAMPLES)

    # tonemap
    beauty_image[:, :, :3] *= 1.0 / 0.6
    beauty_image[:, :, :3] = ACESFilmicToneMapping(beauty_image[:, :, :3])
    # gamma
    beauty_image[:, :, :3] = np.power(
        np.clip(beauty_image[:, :, :3], 0.0, 0.9999), 1.0 / 2.2
    )

    if renderSkybox:
        beauty_ldr = (beauty_image[:, :, :3] * 255).astype(np.uint8)
    else:
        beauty_ldr = (beauty_image * 255).astype(np.uint8)

    save_image(os.path.join("./", outpath), beauty_ldr)
