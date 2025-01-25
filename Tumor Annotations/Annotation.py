import numpy as np
import SimpleITK as sitk
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib
matplotlib.use("TkAgg")

def generate_bounding_boxes(segmentation_array, output_file="bounding_boxes.json"):
    """
    Generate 2D bounding boxes for each slice in a 3D segmentation array.

    Parameters:
        segmentation_array (numpy.ndarray): A 3D numpy array where non-zero values indicate the segmented region.
        output_file (str): Path to save the resulting bounding boxes as a JSON file.

    Returns:
        list: A list of dictionaries containing slice index and bounding box coordinates.
    """
    bounding_boxes = []

    # Iterate through each slice along the Z-axis
    for z in range(segmentation_array.shape[0]):
        slice_array = segmentation_array[z, :, :]  # Extract the 2D slice
        non_zero_coords = np.argwhere(slice_array > 0)  # Find non-zero coordinates

        if non_zero_coords.size > 0:
            # Calculate the bounding box coordinates (min_x, min_y, max_x, max_y)
            min_y, min_x = map(int, np.min(non_zero_coords, axis=0))
            max_y, max_x = map(int, np.max(non_zero_coords, axis=0))
            bounding_boxes.append({
                'slice_index': int(z),
                'bounding_box': [min_x, min_y, max_x, max_y]
            })
        else:
            # No segmentation detected in this slice
            bounding_boxes.append({
                'slice_index': int(z),
                'bounding_box': None
            })

    # Save the bounding boxes to a JSON file
    with open(output_file, "w") as f:
        json.dump(bounding_boxes, f, indent=4)

    print(f"Bounding boxes saved to {output_file}")
    return bounding_boxes


def display_slices_with_bounding_boxes_on_volume(volume_array, segmentation_array, bounding_boxes, num_slices=5):
    """
    Display a limited number of slices from the volume with bounding boxes overlaid.

    Parameters:
        volume_array (numpy.ndarray): The original volume array [Z, Y, X].
        segmentation_array (numpy.ndarray): The segmentation array [Z, Y, X].
        bounding_boxes (list): List of bounding boxes for each slice.
        num_slices (int): Number of slices to display (default: 5).
    """
    # Filter slices with bounding boxes
    slices_with_boxes = [bbox for bbox in bounding_boxes if bbox['bounding_box'] is not None]

    if not slices_with_boxes:
        print("No slices with bounding boxes found.")
        return

    # Limit the number of slices to display
    slices_to_display = slices_with_boxes[num_slices:num_slices + 3]

    num_slices_to_show = len(slices_to_display)
    fig, axes = plt.subplots(1, num_slices_to_show, figsize=(15, 5))

    if num_slices_to_show == 1:  # Handle single slice case
        axes = [axes]

    for ax, bbox_info in zip(axes, slices_to_display):
        slice_index = bbox_info['slice_index']
        bbox = bbox_info['bounding_box']
        volume_slice = volume_array[slice_index, :, :]  # Extract the 2D slice from the original volume
        segmentation_slice = segmentation_array[slice_index, :, :]  # Extract the segmentation slice

        # Display the original volume slice
        ax.imshow(volume_slice, cmap="gray")
        ax.set_title(f"Slice {slice_index}")
        ax.axis("off")

        # Overlay the segmentation for context (optional)
        ax.imshow(segmentation_slice, cmap="jet", alpha=0.3)

        # Overlay the bounding box
        min_x, min_y, max_x, max_y = bbox
        rect = patches.Rectangle((min_x, min_y), max_x - min_x, max_y - min_y,
                                 linewidth=2, edgecolor='red', facecolor='none')
        ax.add_patch(rect)

    plt.tight_layout()
    plt.show()

def main():
    # Main script
    volume_path = r"C:\Tumor Annotation Scans\MRBrainTumor2.nrrd"
    segmentation_path = r"C:\Tumor Annotation Scans\Segmentation.seg.nrrd"

    # Load the volume and segmentation
    volume = sitk.ReadImage(volume_path)
    segmentation = sitk.ReadImage(segmentation_path)

    # Convert to numpy arrays
    volume_array = sitk.GetArrayFromImage(volume)  # [Z, Y, X]
    segmentation_array = sitk.GetArrayFromImage(segmentation)  # [Z, Y, X]

    print(f"Shape of volume: {volume_array.shape}")
    print(f"Shape of segmentation: {segmentation_array.shape}")

    # Generate bounding boxes
    bounding_boxes = generate_bounding_boxes(segmentation_array, output_file="bounding_boxes.json")

    print(f"Generated bounding boxes for {len(bounding_boxes)} slices.")

    # Display a limited number of slices with bounding boxes overlaid on the volume
    num_slices_to_display = 3  # Set the desired number of slices to display
    display_slices_with_bounding_boxes_on_volume(volume_array, segmentation_array, bounding_boxes, num_slices=num_slices_to_display)

if __name__ == "__main__":
    main()
