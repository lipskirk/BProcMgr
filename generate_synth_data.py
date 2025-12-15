import blenderproc as bproc
import random
import json
import colorsys
import numpy as np
import argparse
import os
import bpy
from skimage import measure

parser = argparse.ArgumentParser()
parser.add_argument('-s','--scene', nargs='?', help="Path to the scene.obj file")
parser.add_argument('-o','--output_dir', nargs='?', help="Path to where the final files will be saved")
parser.add_argument('-p','--passes', nargs='?', type = int, default=1, help="Number of rendering passes")
parser.add_argument('-c','--cam_poses', nargs='?', type = int, default=4, help="Number of camera poses in each rendering pass")
parser.add_argument('-d','--DoF_fraction', nargs='?', type = float, default=0, help="Fraction of images rendered with depth of field")
parser.add_argument('-i','--instances', nargs='?', type = int, default=10, help="How many object instances of each simulated category")
parser.add_argument('-t','--categories', nargs='+', type = int, default=12, help="COCO category IDs of simulated objects")
args = parser.parse_args()

bproc.init()

def sample_obj_pose(obj: bproc.types.MeshObject):
    obj.set_location(np.random.uniform([-4, -3, 1], [4, 3, 2]))
    obj.set_rotation_euler(np.random.uniform([0, 0, 0], [0, 0, np.pi * 2]))
    bb = obj.get_bound_box()
    bb_center = np.mean(bb, axis=0)
    bb_min_z_value = np.min(bb, axis=0)[2]
    bottom_point = [bb_center[0], bb_center[1], bb_min_z_value]
    obj.set_origin(bottom_point)
    is_hit, hit_point, _, _, _, _ = bproc.object.scene_ray_cast(origin = bottom_point, direction = [0, 0, -1], max_distance = 4)
    if is_hit :
        obj.set_location(hit_point)

def sample_cam_pose(sphere_center, sphere_radius):
    object_occluded = True
    while object_occluded :
        camera_out_of_range = True
        while camera_out_of_range :
            cam_loc = bproc.sampler.sphere(center = sphere_center, radius = sphere_radius, mode = "SURFACE")
            if np.any(cam_loc <= [-4, -3, 0]) or np.any(cam_loc >= [4, 3, 3]):
                camera_out_of_range = True
                continue
            camera_out_of_range = False
        cam_dir = sphere_center - cam_loc
        is_hit, _, _, _, hit_object, _ = bproc.object.scene_ray_cast(origin = cam_loc, direction = cam_dir)
        if is_hit :
            if hit_object != random_obj :
                object_occluded = True
                continue
            object_occluded = False
    return cam_dir, cam_loc

# Load the objects into the scene
all_objs = bproc.loader.load_blend(args.scene)

# Set default object category
for obj in all_objs :
    obj.set_cp("category_id", 0)

# Read coco categories form file
with open('coco_categories.txt', 'r') as file:
    coco_labels = file.read().splitlines()

# Set category IDs based on object names
chosen_categories = args.categories
for category in chosen_categories :
    if (category < 1) or (category > 91) :
        category = 12
other_categories = []
category_index = -1
for cat in coco_labels :
    category_name = cat.split(':')[0]
    category_index += 1
    if category_index > 0 :
        if category_index not in chosen_categories :
            other_categories.append(category_index)
        category_name = category_name.capitalize()
        category_name = ".*" + category_name + ".*"
        tmp_objs = []
        tmp_objs = bproc.filter.by_attr(all_objs, "name", category_name, regex = True)
        for tmp_obj in tmp_objs :
            tmp_obj.set_cp("category_id", category_index)
        tmp_objs.clear()

# Find objects of selected categories
chosen_objects = []
for category in chosen_categories :
    chosen_objects.extend(bproc.filter.by_cp(all_objs, "category_id", category))

# Duplicate selected objects
duplicated_objects = []
for obj in chosen_objects :
    for n in range(args.instances):
        duplicated_objects.append(obj.duplicate())

# Separate chosen objects, light sources and background objects
lights = bproc.filter.by_attr(all_objs, "name", ".*Light.*", regex = True)
objs_tmp = [x for x in all_objs if x not in lights]
lightplanes = bproc.filter.by_attr(lights, "name", "Light.Plane.*", regex = True)
background_objects = [x for x in objs_tmp if x not in chosen_objects]
objs_tmp.clear()

# Collect materials of all background objects
materials = bproc.material.collect_all()
background_materials = bproc.filter.by_attr(materials, "name", "NE.*",regex = True)
light_materials = bproc.filter.by_attr(materials, "name", "Light.*", regex = True)

#Define camera resolution and renderer parameters
bproc.camera.set_resolution(640, 640)
bproc.renderer.set_noise_threshold(0.1)
bproc.renderer.set_light_bounces(ao_bounces_render = 2)
DoF_passes = args.DoF_fraction*args.passes
CoC = 0.03

pass_number = 0
# Randomize scene parameters and render with multiple camera poses
for r in range(args.passes) :
    pass_number += 1
    bproc.utility.reset_keyframes()

    # Randomize background color and exposure level
    hue_cold = np.random.uniform(0.5, 0.6)
    hue_warm = np.random.uniform(0.04, 0.12)
    saturation = np.random.uniform(0, 1)
    value = np.random.uniform(0.8, 1)
    if np.random.uniform(0,1) > 0.5 :
        color_rgb = colorsys.hsv_to_rgb(hue_cold,saturation,value)
    else :
        color_rgb = colorsys.hsv_to_rgb(hue_warm,saturation,value)
    bproc.renderer.set_world_background(list(255*np.array(color_rgb)), np.random.uniform(0, 0.001))
    bproc.renderer.set_output_format(exposure = np.random.normal(0, 1))

    # Randomize camera intrinsics
    x0 = np.random.normal(320, 100)
    y0 = np.random.normal(320, 100)
    f0 = np.random.uniform(350, 1500)
    orig_res_x, orig_res_y = 640, 640
    cam_K = np.array([[f0, 0.0, x0], [0.0, f0, y0], [0.0, 0.0, 1.0]])
    bproc.camera.set_intrinsics_from_K_matrix(
                cam_K,
                orig_res_x,
                orig_res_y,
                bpy.context.scene.camera.data.clip_start,
                bpy.context.scene.camera.data.clip_end
            )

    # Randomize duplicated objects poses
    bproc.object.sample_poses(
                duplicated_objects,
                sample_pose_func = sample_obj_pose,
                objects_to_check_collisions = all_objs
            )

    # Randomize materials of all background objects
    for obj in background_objects:
        for i in range(len(obj.get_materials())):
            if np.random.uniform(0, 1) <= 0.5:
                obj.set_material(i, random.choice(background_materials))

    # Randomize positions and emmisive materials of light sources
    for obj in lights:
        for i in range(len(obj.get_materials())):
            if np.random.uniform(0, 1) <= 0.5:
                obj.set_material(i, random.choice(light_materials))
    for lightplane in lightplanes :
        lightplane.set_location(np.random.uniform([-2, -30, 3], [5, -3, 5]))

    # With DoF activated 
    if pass_number <= DoF_passes :        
        # Choose random object of selected category and calculate point of interest
        random_obj = (np.random.choice(duplicated_objects))
        random_obj_list = [random_obj]
        poi = bproc.object.compute_poi(random_obj_list)

        # Set focus point and initial camera DoF parameters
        focus_point = bproc.object.create_empty("Camera Focus Point")
        focus_point.set_location(poi)
        min_cam_distance = 1000

        # Sample camera poses
        for i in range(int(args.cam_poses / 2)) :
            # Randomize camera position, while ensuring selected object can be seen
            cam_distance = np.random.uniform(0.1, 3)
            cam_direction, cam_location = sample_cam_pose(poi, cam_distance)

            # Set fstop to regulate the sharpness of the scene
            if cam_distance < min_cam_distance :
                focal_length = f0 / 100
                real_distance = cam_distance * 1000
                f_stop = (focal_length ** 2) / (CoC * (real_distance - focal_length))
                bproc.camera.add_depth_of_field(focus_point, fstop_value = np.random.normal(f_stop, f_stop / 8))
                min_cam_distance = cam_distance

            # Add homog cam pose based on location an rotation
            rotation_matrix = bproc.camera.rotation_from_forward_vec(cam_direction)
            cam2world_matrix = bproc.math.build_transformation_mat(cam_location, rotation_matrix)
            bproc.camera.add_camera_pose(cam2world_matrix)

    # Without DoF activated 
    else :
        # Sample camera poses
        for i in range(args.cam_poses) :
            # Choose random object of selected category  and calculate point of interest
            random_obj = np.random.choice(duplicated_objects)
            random_obj_list = [random_obj]
            poi = bproc.object.compute_poi(random_obj_list)
                        
            # Randomize camera position, while ensuring selected object can be seen
            camera_distance = np.random.uniform(0.1, 3)
            cam_direction, cam_location = sample_cam_pose(poi, camera_distance)
            
            # Deactivate depth of field
            bpy.context.scene.camera.data.dof.use_dof = False
            
            # Add homog cam pose based on location an rotation
            rotation_matrix = bproc.camera.rotation_from_forward_vec(cam_direction)
            cam2world_matrix = bproc.math.build_transformation_mat(cam_location, rotation_matrix)
            bproc.camera.add_camera_pose(cam2world_matrix)

    # Activate instance segmentation rendering
    bproc.renderer.enable_segmentation_output(map_by = ["instance", "category_id"])
    
    # Render the whole pipeline
    data = bproc.renderer.render()

    # Write the data to a .hdf5 container
    bproc.writer.write_hdf5(args.output_dir, data, append_to_existing_output = True)

    # Write data to coco file
    bproc.writer.write_coco_annotations(os.path.join(args.output_dir, 'coco_data'),
                                    instance_segmaps=data["instance_segmaps"],
                                    instance_attribute_maps=data["instance_attribute_maps"],
                                    colors=data["colors"],
                                    color_file_format="JPEG")
    
with open(os.path.join(args.output_dir, 'coco_data\coco_annotations.json'), 'r') as labels_input:
    data_input = json.load(labels_input)

# Convert segmentation format from RLE to polygons
for annotation in data_input["annotations"] :
    zeros_array = np.zeros(640 * 640)
    rle_array = np.array(zeros_array, dtype = bool)
    
    # Get binary mask from RLE
    fill = False
    distance = 0
    for segment in annotation["segmentation"]["counts"] :
        if fill is False:
            distance = distance + segment
            fill = True
        else :
            for i in range(segment) :
                rle_array[distance] = 1
                distance += 1
            fill = False
    binary_mask_preT = np.zeros((640, 640), dtype = bool)
    for row in range(640) :
        for pixel in range (640) :
            binary_mask_preT[row][pixel] = rle_array[640 * row + pixel]
    binary_mask = binary_mask_preT.T

    # Convert binary mask to polygons
    polygons = []
    contours = measure.find_contours(binary_mask, 0.5)
    for contour in contours:
        contour = bproc.python.writer.CocoWriterUtility._CocoWriterUtility.close_contour(contour)
        polygon = measure.approximate_polygon(contour, 0)
        if len(polygon) < 3:
            continue
        polygon = np.flip(polygon, axis=1)
        polygon = polygon.ravel()
        polygon[polygon < 0] = 0
        polygons.append(polygon.tolist())
    annotation["segmentation"] = polygons

# Fix filenames and COCO categories
for image in data_input["images"] :
    image["file_name"] = image["file_name"].removeprefix("images/")
json_categories = []
id_count = -1
for label in coco_labels :
    id_count += 1
    json_categories.append({"id" : id_count, "supercategory" : label.split(':')[1], "name" : label.split(':')[0]})
data_input["categories"] = json_categories
with open(os.path.join(args.output_dir, 'coco_data\coco_annotations2.json'), 'w') as output_file:
    json.dump(data_input, output_file)
