# math/science imports
import numpy as np


def from_HU_to_normal(img):
    """
    Converts image in Hounsfield Units (air-> -1000, bone->500) into a [0-1] image. 
    Comercial scanners use a piecewise linear function. Check STIR for real values. (https://raw.githubusercontent.com/UCL/STIR/85cc1940c297b1749cf44a9fba937d7cefdccd47/src/utilities/share/ct_slopes.json)
    """
    return np.maximum((img + 1000) / 3000, 0)

def from_HU_to_mu(img):
    """
    Converts image in Hounsfield Units (air-> -1000, bone->500) into linear attenuation coefficient (air-> 0.0012, 
    bone->1.52 g/cm^3). Approximate. 
    Comercial scanners use a piecewise linear function. Check STIR for real values. (https://raw.githubusercontent.com/UCL/STIR/85cc1940c297b1749cf44a9fba937d7cefdccd47/src/utilities/share/ct_slopes.json)
    """
    return ((1.52 - 0.0012) / (500 + 1000)) * (img.astype(np.float32) + 1000) + 0.0012


def sinogram_add_noise(proj, I0=1000, sigma=5,crosstalk=0.05,flat_field=None,dark_field=None):
    """
    Adds realistic noise to sinograms.
    - Poisson noise, with I0 counts in a scanner with no sample (bigger value==less noise)
    - Gaussian noise of zero mean and sigma std
    - Detector crosstalk in % of the signal of adjacent pixels.
    - Add a flat_field to add even more realistic noise (computed at non-corrected flat fields)
    """
    if dark_field is None:
        dark_field=np.zeros(proj.shape)
    if flat_field is None:
        flat_field=np.ones(proj.shape)*np.amax(proj)

    max_val=np.amax(flat_field) # alternatively the highest power of 2 close to this value, but lets leave it as is. 
    
    Im=I0*np.exp(-proj/max_val)
    flat_field=I0*np.exp(-flat_field/max_val)
    dark_field=I0*np.exp(-dark_field/max_val)
    # Uncorrect the flat fields
    Im=Im*(flat_field-dark_field)+dark_field

    # Add noise
    Im= np.random.poisson(Im)  + sigma * np.random.standard_normal(size=Im.shape)
   
    # Detector cross talk
    cross=[crosstalk,1,crosstalk]
    for ax in range(1,len(proj.shape)):
        Im=np.apply_along_axis(lambda m: np.convolve(m, cross, mode='full'), axis=ax, arr=Im)

    Im[Im<=0]=1e-6
    # Correct flat fields
    Im=(Im-dark_field)/(flat_field-dark_field)
    return -np.log(Im/I0)*max_val


def from_HU_to_material_id(img):
    """
    Converts an image in Hounsfield units into a material index
    May require some image filtering preprocessing
    """
    materials = img
    materials[img < -950] = 0  # air
    materials[(img > -950) & (img < -750)] = 1  # lung
    materials[(img > -750) & (img < -150)] = 2  # bronqui
    materials[(img > -150) & (img < -0)] = 3  # fat
    materials[(img > 0) & (img < 150)] = 4  # muscle
    materials[(img > 150) & (img < 300)] = 5  # bone marrow
    materials[img > 300] = 6  # bone
    materials = materials.astype(np.uint8)
    return materials


def forward_projection_fan(image,size,sino_shape,sino_size,DSD,DSO,backend="tomosipo",angles=360):
    """
    Produces a noise free forward projection, given np.array image, a size (in real world units), a sinogram shape and size,
    distances from source to detector DSD and distance from source to object DSO. 
    May support other backends than tomosipo
    """

    if backend != "tomosipo":
        raise ValueError("Only tomosipo backend for CT supported")
    # You can add other backends here
    import tomosipo as ts

    if len(image.shape)==3:
        if image.shape[0]>1: # there is no reason to have this constraint
            raise ValueError("Image must be 2D")
    elif len(image.shape)==2:
        image=np.expand_dims(image,axis=0)
    else:
        raise ValueError("Image must be 2D")

    if isinstance(size,list) or isinstance(size,np.ndarray):
        size=tuple(size)
    if isinstance(sino_shape,list) or isinstance(sino_shape,np.ndarray):
        size=tuple(sino_shape)
    if isinstance(sino_size,list) or isinstance(sino_size,np.ndarray):
        size=tuple(sino_size)

    vg = ts.volume(shape=image.shape, size=size)
    pg = ts.cone(angles=angles, shape=sino_shape, size=sino_size, src_orig_dist=DSO, src_det_dist=DSD)
    A = ts.operator(vg, pg)
    return A(np.expand_dims(image,axis=0))[0]



