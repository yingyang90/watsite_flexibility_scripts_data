### watsite_flexibility_scripts_data

#### Step 1: run a long free MD simulation for the system (with or without ligand)
* for protein-ligand complex, use the openmm_prep.py to define the interactions to be restrained
* cluster the trajectory based on BindingSite rmsd
  * ``` pymol -c getBindingSiteResi.pml``` will generate bs_res.txt, and modify cpptraj_\*.in files with correct binding site residue numbers
  * align trajectory: ``` cpptraj < 1_cpptraj_traj.in```
  * cluster trajectory: ``` cpptraj < 2_cpptraj_cluster.in ``` --> cluster_hier.c? will be generated for the clusters
* redo clustering for the top 10 clusters using the runCpptraj.py script
```python runCpptraj.py -c``` --> generate rep_c?.c?.pdb
* plot 2drmsd.gnu for the top 10 clusters
```python runCpptraj.py -r``` --> generate rms2d_10cluster.gnu
* For each cluster of interest, extract the conformation based on the frame number 
```python runCpptraj.py -f hier.4_summary_sieve10.txt c0_summary.txt ```
```python runCpptraj.py -f hier.4_summary_sieve10.txt c1_summary.txt ```
```python runCpptraj.py -f hier.4_summary_sieve10.txt c4_summary.txt ```

#### Step 2: rerun short (5ns) WATsite for each subcluster from cluster
* cluster folder created from extraction of previous long trajectory
* run WATsite docker, and run python in the folder contains all cluster folder
```
python subAll.py
```

#### Analysis Scripts and Brief Usage
* to generate an rms2d plot and RMSF values for binding site residues throughout a simulation, run  ``` cpptraj < cpptraj_rmsf.in ```
* analyze hydration site predictions from all subclusters by running ``` python analyzeAllHS.py ``` Produces graph with HS sites identified as pairs and generates by_[0-10].pdb files
* for grid analysis, use combineDX.py to generate mean density, standard deviation, and max error dx grids
* to test the convergence of a system, use egy_convergence.py to compare the energies from the first frames to the entire trajectory. This script can also compare energies between different simulations (restrained vs unrestrained)
* plotHist.py can also be used to test the positional convergence of hydration site predictions and to compare against crystal waters
* plotPerHSenthalpy.py script can be used to vizualize the enthalpy values of each HS through out the trajectory. Useful when there is a large range of enthalpy.

#### Collected Data for Publication
##### HSP90
###### Restrained RMSD
* k[0.6-4.8]rms2d.png RMS of BS residues throughout restrained simulations

###### Cluster Subcluster
* FigureC[0,1,7].png Clustered hydration sites using ten subclusters

##### Klebe
* k[1.2-5]rms2d.png RMS of BS residues throughout restrained simulations