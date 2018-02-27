
# prepare the system from amber files
# YY modified openmm_prep.py for prot-lig restraint
if [ ! -f sys_min.xml ]; then
/usr/local/anaconda/bin/python ./openmm_prep.py \
-i prot_fixed.inpcrd -t prot_fixed.prmtop \
--cuda 1 -l PME -c 10.00 --shake \
--restrain-mask '!:HOH,WAT,NA,CL&!@H=' -k 10.0 --reference prot_fixed.pdb
fi

# temperature coupling 298.15 K: 25,000 * 1.0 fs = 25 ps
if [ ! -f sys_NVT.xml ]; then
/usr/local/anaconda/bin/python /home/downloads/WATsite3.0/bin/openmm_md.py \
-i prot_fixed.inpcrd -t prot_fixed.prmtop \
--xml system.xml -s sys_min.xml --restart sys_NVT.xml \
-x sys_NVT.nc -r sys_NVT.info -o sys_NVT.out \
--temp 298.15 --gamma_ln 1.0 -n 25000 --interval 1000 --dt 1.0 \
--restrain-mask '!:WAT&!@H=' -k 4.8 --reference prot_fixed.pdb \
--cuda 1
fi

# pressure coupling 298.15 K and 1 bar: 500000 (stpes) * 2.0 (timestep fs) = 1000.0 ps = 1.0 ns
if [ ! -f sys_NPT.xml ]; then
/usr/local/anaconda/bin/python /home/downloads/WATsite3.0/bin/openmm_md.py \
-i prot_fixed.inpcrd -t prot_fixed.prmtop \
--xml system.xml -s sys_NVT.xml --restart sys_NPT.xml \
-x sys_NPT.nc -r sys_NPT.info -o sys_NPT.out \
--temp 298.15 --gamma_ln 1.0 -n 500000 --interval 10000 --dt 2.0 \
--restrain-mask '!:WAT&!@H=' -k 4.8 --reference prot_fixed.pdb \
--cuda 1 --npt
fi

# production run 298.15 K and 1 bar: 500000 (stpes) * 2.0 (timestep fs) = 1000.0 ps = 1.0 ns * 5
if [ ! -f sys_md_1.xml ]; then
/usr/local/anaconda/bin/python /home/downloads/WATsite3.0/bin/openmm_md.py \
-i prot_fixed.inpcrd -t prot_fixed.prmtop \
--xml system.xml -s sys_NPT.xml --restart sys_md_1.xml \
-x sys_md_1.nc  -r sys_md_1.info  -o sys_md_1.out \
--temp 298.15 --gamma_ln 1.0 -n 1000000 --interval 1000 --dt 2.0 \
-p prot_fixed.pdb --cuda 1 --npt
fi

if [ ! -f sys_md_2.xml ]; then
/usr/local/anaconda/bin/python /home/downloads/WATsite3.0/bin/openmm_md.py \
-i prot_fixed.inpcrd -t prot_fixed.prmtop \
--xml system.xml -s sys_md_1.xml --restart sys_md_2.xml \
-x sys_md_2.nc  -r sys_md_2.info  -o sys_md_2.out \
--temp 298.15 --gamma_ln 1.0 -n 1000000 --interval 1000 --dt 2.0 \
-p prot_fixed.pdb --cuda 1 --npt
fi

if [ ! -f sys_md_3.xml ]; then
/usr/local/anaconda/bin/python /home/downloads/WATsite3.0/bin/openmm_md.py \
-i prot_fixed.inpcrd -t prot_fixed.prmtop \
--xml system.xml -s sys_md_2.xml --restart sys_md_3.xml \
-x sys_md_3.nc  -r sys_md_3.info  -o sys_md_3.out \
--temp 298.15 --gamma_ln 1.0 -n 1000000 --interval 1000 --dt 2.0 \
-p prot_fixed.pdb --cuda 1 --npt
fi

if [ ! -f sys_md_4.xml ]; then
/usr/local/anaconda/bin/python /home/downloads/WATsite3.0/bin/openmm_md.py \
-i prot_fixed.inpcrd -t prot_fixed.prmtop \
--xml system.xml -s sys_md_3.xml --restart sys_md_4.xml \
-x sys_md_4.nc  -r sys_md_4.info  -o sys_md_4.out \
--temp 298.15 --gamma_ln 1.0 -n 1000000 --interval 1000 --dt 2.0 \
-p prot_fixed.pdb --cuda 1 --npt
fi

if [ ! -f sys_md_5.xml ]; then
/usr/local/anaconda/bin/python /home/downloads/WATsite3.0/bin/openmm_md.py \
-i prot_fixed.inpcrd -t prot_fixed.prmtop \
--xml system.xml -s sys_md_4.xml --restart sys_md_5.xml \
-x sys_md_5.nc  -r sys_md_5.info  -o sys_md_5.out \
--temp 298.15 --gamma_ln 1.0 -n 1000000 --interval 1000 --dt 2.0 \
-p prot_fixed.pdb --cuda 1 --npt
fi


# production run 298.15 K and 1 bar: 1000000 (steps) * 2 (timestep fs) = 2000 ps = 2 ns
if [ ! -f sys_md_6.xml ]; then
/usr/local/anaconda/bin/python /home/downloads/WATsite3.0/bin/openmm_md.py \
-i prot_fixed.inpcrd -t prot_fixed.prmtop \
--xml system.xml -s sys_md_5.xml --restart sys_md_6.xml \
-x sys_md_6.nc  -r sys_md_6.info  -o sys_md_6.out \
--temp 298.15 --gamma_ln 1.0 -n 1000000 --interval 1000 --dt 2 \
--cuda 1 --npt
fi

# production run 298.15 K and 1 bar: 1000000 (steps) * 2 (timestep fs) = 2000 ps = 2 ns
if [ ! -f sys_md_7.xml ]; then
/usr/local/anaconda/bin/python /home/downloads/WATsite3.0/bin/openmm_md.py \
-i prot_fixed.inpcrd -t prot_fixed.prmtop \
--xml system.xml -s sys_md_6.xml --restart sys_md_7.xml \
-x sys_md_7.nc  -r sys_md_7.info  -o sys_md_7.out \
--temp 298.15 --gamma_ln 1.0 -n 1000000 --interval 1000 --dt 2 \
--cuda 1 --npt
fi

# production run 298.15 K and 1 bar: 1000000 (steps) * 2 (timestep fs) = 2000 ps = 2 ns
if [ ! -f sys_md_8.xml ]; then
/usr/local/anaconda/bin/python /home/downloads/WATsite3.0/bin/openmm_md.py \
-i prot_fixed.inpcrd -t prot_fixed.prmtop \
--xml system.xml -s sys_md_7.xml --restart sys_md_8.xml \
-x sys_md_8.nc  -r sys_md_8.info  -o sys_md_8.out \
--temp 298.15 --gamma_ln 1.0 -n 1000000 --interval 1000 --dt 2 \
--cuda 1 --npt
fi

# production run 298.15 K and 1 bar: 1000000 (steps) * 2 (timestep fs) = 2000 ps = 2 ns
if [ ! -f sys_md_9.xml ]; then
/usr/local/anaconda/bin/python /home/downloads/WATsite3.0/bin/openmm_md.py \
-i prot_fixed.inpcrd -t prot_fixed.prmtop \
--xml system.xml -s sys_md_8.xml --restart sys_md_9.xml \
-x sys_md_9.nc  -r sys_md_9.info  -o sys_md_9.out \
--temp 298.15 --gamma_ln 1.0 -n 1000000 --interval 1000 --dt 2 \
--cuda 1 --npt
fi

# production run 298.15 K and 1 bar: 1000000 (steps) * 2 (timestep fs) = 2000 ps = 2 ns
if [ ! -f sys_md_10.xml ]; then
/usr/local/anaconda/bin/python /home/downloads/WATsite3.0/bin/openmm_md.py \
-i prot_fixed.inpcrd -t prot_fixed.prmtop \
--xml system.xml -s sys_md_9.xml --restart sys_md_10.xml \
-x sys_md_10.nc  -r sys_md_10.info  -o sys_md_10.out \
--temp 298.15 --gamma_ln 1.0 -n 1000000 --interval 1000 --dt 2 \
--cuda 1 --npt
fi

# production run 298.15 K and 1 bar: 1000000 (steps) * 2 (timestep fs) = 2000 ps = 2 ns
if [ ! -f sys_md_11.xml ]; then
/usr/local/anaconda/bin/python /home/downloads/WATsite3.0/bin/openmm_md.py \
-i prot_fixed.inpcrd -t prot_fixed.prmtop \
--xml system.xml -s sys_md_10.xml --restart sys_md_11.xml \
-x sys_md_11.nc  -r sys_md_11.info  -o sys_md_11.out \
--temp 298.15 --gamma_ln 1.0 -n 1000000 --interval 1000 --dt 2 \
--cuda 1 --npt
fi

# production run 298.15 K and 1 bar: 1000000 (steps) * 2 (timestep fs) = 2000 ps = 2 ns
if [ ! -f sys_md_12.xml ]; then
/usr/local/anaconda/bin/python /home/downloads/WATsite3.0/bin/openmm_md.py \
-i prot_fixed.inpcrd -t prot_fixed.prmtop \
--xml system.xml -s sys_md_11.xml --restart sys_md_12.xml \
-x sys_md_12.nc  -r sys_md_12.info  -o sys_md_12.out \
--temp 298.15 --gamma_ln 1.0 -n 1000000 --interval 1000 --dt 2 \
--cuda 1 --npt
fi

# production run 298.15 K and 1 bar: 1000000 (steps) * 2 (timestep fs) = 2000 ps = 2 ns
if [ ! -f sys_md_13.xml ]; then
/usr/local/anaconda/bin/python /home/downloads/WATsite3.0/bin/openmm_md.py \
-i prot_fixed.inpcrd -t prot_fixed.prmtop \
--xml system.xml -s sys_md_12.xml --restart sys_md_13.xml \
-x sys_md_13.nc  -r sys_md_13.info  -o sys_md_13.out \
--temp 298.15 --gamma_ln 1.0 -n 1000000 --interval 1000 --dt 2 \
--cuda 1 --npt
fi

# production run 298.15 K and 1 bar: 1000000 (steps) * 2 (timestep fs) = 2000 ps = 2 ns
if [ ! -f sys_md_14.xml ]; then
/usr/local/anaconda/bin/python /home/downloads/WATsite3.0/bin/openmm_md.py \
-i prot_fixed.inpcrd -t prot_fixed.prmtop \
--xml system.xml -s sys_md_13.xml --restart sys_md_14.xml \
-x sys_md_14.nc  -r sys_md_14.info  -o sys_md_14.out \
--temp 298.15 --gamma_ln 1.0 -n 1000000 --interval 1000 --dt 2 \
--cuda 1 --npt
fi

# production run 298.15 K and 1 bar: 1000000 (steps) * 2 (timestep fs) = 2000 ps = 2 ns
if [ ! -f sys_md_15.xml ]; then
/usr/local/anaconda/bin/python /home/downloads/WATsite3.0/bin/openmm_md.py \
-i prot_fixed.inpcrd -t prot_fixed.prmtop \
--xml system.xml -s sys_md_14.xml --restart sys_md_15.xml \
-x sys_md_15.nc  -r sys_md_15.info  -o sys_md_15.out \
--temp 298.15 --gamma_ln 1.0 -n 1000000 --interval 1000 --dt 2 \
--cuda 1 --npt
fi

# production run 298.15 K and 1 bar: 1000000 (steps) * 2 (timestep fs) = 2000 ps = 2 ns
if [ ! -f sys_md_16.xml ]; then
/usr/local/anaconda/bin/python /home/downloads/WATsite3.0/bin/openmm_md.py \
-i prot_fixed.inpcrd -t prot_fixed.prmtop \
--xml system.xml -s sys_md_15.xml --restart sys_md_16.xml \
-x sys_md_16.nc  -r sys_md_16.info  -o sys_md_16.out \
--temp 298.15 --gamma_ln 1.0 -n 1000000 --interval 1000 --dt 2 \
--cuda 1 --npt
fi

# production run 298.15 K and 1 bar: 1000000 (steps) * 2 (timestep fs) = 2000 ps = 2 ns
if [ ! -f sys_md_17.xml ]; then
/usr/local/anaconda/bin/python /home/downloads/WATsite3.0/bin/openmm_md.py \
-i prot_fixed.inpcrd -t prot_fixed.prmtop \
--xml system.xml -s sys_md_16.xml --restart sys_md_17.xml \
-x sys_md_17.nc  -r sys_md_17.info  -o sys_md_17.out \
--temp 298.15 --gamma_ln 1.0 -n 1000000 --interval 1000 --dt 2 \
--cuda 1 --npt
fi

# production run 298.15 K and 1 bar: 1000000 (steps) * 2 (timestep fs) = 2000 ps = 2 ns
if [ ! -f sys_md_18.xml ]; then
/usr/local/anaconda/bin/python /home/downloads/WATsite3.0/bin/openmm_md.py \
-i prot_fixed.inpcrd -t prot_fixed.prmtop \
--xml system.xml -s sys_md_17.xml --restart sys_md_18.xml \
-x sys_md_18.nc  -r sys_md_18.info  -o sys_md_18.out \
--temp 298.15 --gamma_ln 1.0 -n 1000000 --interval 1000 --dt 2 \
--cuda 1 --npt
fi

# production run 298.15 K and 1 bar: 1000000 (steps) * 2 (timestep fs) = 2000 ps = 2 ns
if [ ! -f sys_md_19.xml ]; then
/usr/local/anaconda/bin/python /home/downloads/WATsite3.0/bin/openmm_md.py \
-i prot_fixed.inpcrd -t prot_fixed.prmtop \
--xml system.xml -s sys_md_18.xml --restart sys_md_19.xml \
-x sys_md_19.nc  -r sys_md_19.info  -o sys_md_19.out \
--temp 298.15 --gamma_ln 1.0 -n 1000000 --interval 1000 --dt 2 \
--cuda 1 --npt
fi

# production run 298.15 K and 1 bar: 1000000 (steps) * 2 (timestep fs) = 2000 ps = 2 ns
if [ ! -f sys_md_20.xml ]; then
/usr/local/anaconda/bin/python /home/downloads/WATsite3.0/bin/openmm_md.py \
-i prot_fixed.inpcrd -t prot_fixed.prmtop \
--xml system.xml -s sys_md_19.xml --restart sys_md_20.xml \
-x sys_md_20.nc  -r sys_md_20.info  -o sys_md_20.out \
--temp 298.15 --gamma_ln 1.0 -n 1000000 --interval 1000 --dt 2 \
--cuda 1 --npt
fi

# production run 298.15 K and 1 bar: 1000000 (steps) * 2 (timestep fs) = 2000 ps = 2 ns
if [ ! -f sys_md_21.xml ]; then
/usr/local/anaconda/bin/python /home/downloads/WATsite3.0/bin/openmm_md.py \
-i prot_fixed.inpcrd -t prot_fixed.prmtop \
--xml system.xml -s sys_md_20.xml --restart sys_md_21.xml \
-x sys_md_21.nc  -r sys_md_21.info  -o sys_md_21.out \
--temp 298.15 --gamma_ln 1.0 -n 1000000 --interval 1000 --dt 2 \
--cuda 1 --npt
fi

# production run 298.15 K and 1 bar: 1000000 (steps) * 2 (timestep fs) = 2000 ps = 2 ns
if [ ! -f sys_md_22.xml ]; then
/usr/local/anaconda/bin/python /home/downloads/WATsite3.0/bin/openmm_md.py \
-i prot_fixed.inpcrd -t prot_fixed.prmtop \
--xml system.xml -s sys_md_21.xml --restart sys_md_22.xml \
-x sys_md_22.nc  -r sys_md_22.info  -o sys_md_22.out \
--temp 298.15 --gamma_ln 1.0 -n 1000000 --interval 1000 --dt 2 \
--cuda 1 --npt
fi

# production run 298.15 K and 1 bar: 1000000 (steps) * 2 (timestep fs) = 2000 ps = 2 ns
if [ ! -f sys_md_23.xml ]; then
/usr/local/anaconda/bin/python /home/downloads/WATsite3.0/bin/openmm_md.py \
-i prot_fixed.inpcrd -t prot_fixed.prmtop \
--xml system.xml -s sys_md_22.xml --restart sys_md_23.xml \
-x sys_md_23.nc  -r sys_md_23.info  -o sys_md_23.out \
--temp 298.15 --gamma_ln 1.0 -n 1000000 --interval 1000 --dt 2 \
--cuda 1 --npt
fi

# production run 298.15 K and 1 bar: 1000000 (steps) * 2 (timestep fs) = 2000 ps = 2 ns
if [ ! -f sys_md_24.xml ]; then
/usr/local/anaconda/bin/python /home/downloads/WATsite3.0/bin/openmm_md.py \
-i prot_fixed.inpcrd -t prot_fixed.prmtop \
--xml system.xml -s sys_md_23.xml --restart sys_md_24.xml \
-x sys_md_24.nc  -r sys_md_24.info  -o sys_md_24.out \
--temp 298.15 --gamma_ln 1.0 -n 1000000 --interval 1000 --dt 2 \
--cuda 1 --npt
fi

# production run 298.15 K and 1 bar: 1000000 (steps) * 2 (timestep fs) = 2000 ps = 2 ns
if [ ! -f sys_md_25.xml ]; then
/usr/local/anaconda/bin/python /home/downloads/WATsite3.0/bin/openmm_md.py \
-i prot_fixed.inpcrd -t prot_fixed.prmtop \
--xml system.xml -s sys_md_24.xml --restart sys_md_25.xml \
-x sys_md_25.nc  -r sys_md_25.info  -o sys_md_25.out \
--temp 298.15 --gamma_ln 1.0 -n 1000000 --interval 1000 --dt 2 \
--cuda 1 --npt
fi

