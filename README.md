# AI tools for learned tomographic reconstruction

University of Cambridge Computational Image Analysis (CIA) groups AI tools for tomographic reconstruction. 


**WARNING** Building in progress. 

Install: (this is a temporary list, we will clean it up)

```
conda install pytorch torchvision torchaudio pytorch-cuda=11.6 -c pytorch -c nvidia
conda install cudatoolkit=11.6 tomosipo tqdm pytorch matplotlib -c pytorch -c astra-toolbox -c aahendriksen -c defaults -c conda-forge
pip install git+https://github.com/ahendriksen/ts_algorithms.git
conda install scikit-image
conda install pip
/local/scratch/public/<yourusername>/anaconda3/envs/aitools/bin/pip3 install pydicom
conda install natsort h5py
conda install -c simpleitk simpleitk
```


# Developers:
Read `developers.md`