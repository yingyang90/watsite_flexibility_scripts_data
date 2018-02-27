pwd

# prepare the system from amber files
if [ ! -f sys_min.xml ]; then
/usr/local/anaconda/bin/python /home/downloads/WATsite3.0/bin/openmm_prep.py  -i prot_amber.inpcrd -t prot_amber.prmtop \
--cuda 1 -l PME -c 10.00 --shake \
--restrain-mask '!:WAT&!@H=' -k 10.0 --reference prot_amber.pdb
fi

# temperature coupling 298.15 K: 25,000 * 1.0 fs = 25 ps
if [ ! -f sys_NVT.xml ]; then
/usr/local/anaconda/bin/python /home/downloads/WATsite3.0/bin/openmm_md.py  -i prot_amber.inpcrd -t prot_amber.prmtop \
--xml system.xml -s sys_min.xml --restart sys_NVT.xml \
-x sys_NVT.nc -r sys_NVT.info -o sys_NVT.out \
--temp 298.15 --gamma_ln 1.0 -n 25000 --interval 1000 --dt 1.0 \
--restrain-mask '!:WAT&!@H=' -k 4.8 --reference prot_amber.pdb \
--cuda 1
fi

# pressure coupling 298.15 K and 1 bar: 500000 (stpes) * 2.0 (timestep fs) = 1000.0 ps = 1.0 ns
if [ ! -f sys_NPT.xml ]; then
/usr/local/anaconda/bin/python /home/downloads/WATsite3.0/bin/openmm_md.py  -i prot_amber.inpcrd -t prot_amber.prmtop \
--xml system.xml -s sys_NVT.xml --restart sys_NPT.xml \
-x sys_NPT.nc -r sys_NPT.info -o sys_NPT.out \
--temp 298.15 --gamma_ln 1.0 -n 500000 --interval 10000 --dt 2.0 \
--restrain-mask '!:WAT&!@H=' -k 4.8 --reference prot_amber.pdb \
--cuda 1 --npt
fi


# production run 298.15 K and 1 bar: 500000 (stpes) * 2.0 (timestep fs) = 1000.0 ps = 1.0 ns * 5
if [ ! -f sys_md_1.xml ]; then
/usr/local/anaconda/bin/python /home/downloads/WATsite3.0/bin/openmm_md.py  -i prot_amber.inpcrd -t prot_amber.prmtop \
--xml system.xml -s sys_NPT.xml --restart sys_md_1.xml \
-x sys_md_1.nc  -r sys_md_1.info  -o sys_md_1.out \
--temp 298.15 --gamma_ln 1.0 -n 500000 --interval 500 --dt 2.0 \
--restrain-mask '!:WAT&!@H=' -k 4.8 --reference prot_amber.pdb \
--water SPC/E --prev_frame 0 -p prot_amber.pdb --cuda 1 --npt
fi

if [ ! -f sys_md_2.xml ]; then
/usr/local/anaconda/bin/python /home/downloads/WATsite3.0/bin/openmm_md.py  -i prot_amber.inpcrd -t prot_amber.prmtop \
--xml system.xml -s sys_md_1.xml --restart sys_md_2.xml \
-x sys_md_2.nc  -r sys_md_2.info  -o sys_md_2.out \
--temp 298.15 --gamma_ln 1.0 -n 500000 --interval 500 --dt 2.0 \
--restrain-mask '!:WAT&!@H=' -k 4.8 --reference prot_amber.pdb \
--water SPC/E --prev_frame 1000 -p prot_amber.pdb --cuda 1 --npt
fi

if [ ! -f sys_md_3.xml ]; then
/usr/local/anaconda/bin/python /home/downloads/WATsite3.0/bin/openmm_md.py  -i prot_amber.inpcrd -t prot_amber.prmtop \
--xml system.xml -s sys_md_2.xml --restart sys_md_3.xml \
-x sys_md_3.nc  -r sys_md_3.info  -o sys_md_3.out \
--temp 298.15 --gamma_ln 1.0 -n 500000 --interval 500 --dt 2.0 \
--restrain-mask '!:WAT&!@H=' -k 4.8 --reference prot_amber.pdb \
--water SPC/E --prev_frame 2000 -p prot_amber.pdb --cuda 1 --npt
fi

if [ ! -f sys_md_4.xml ]; then
/usr/local/anaconda/bin/python /home/downloads/WATsite3.0/bin/openmm_md.py  -i prot_amber.inpcrd -t prot_amber.prmtop \
--xml system.xml -s sys_md_3.xml --restart sys_md_4.xml \
-x sys_md_4.nc  -r sys_md_4.info  -o sys_md_4.out \
--temp 298.15 --gamma_ln 1.0 -n 500000 --interval 500 --dt 2.0 \
--restrain-mask '!:WAT&!@H=' -k 4.8 --reference prot_amber.pdb \
--water SPC/E --prev_frame 3000 -p prot_amber.pdb --cuda 1 --npt
fi

if [ ! -f sys_md_5.xml ]; then
/usr/local/anaconda/bin/python /home/downloads/WATsite3.0/bin/openmm_md.py  -i prot_amber.inpcrd -t prot_amber.prmtop \
--xml system.xml -s sys_md_4.xml --restart sys_md_5.xml \
-x sys_md_5.nc  -r sys_md_5.info  -o sys_md_5.out \
--temp 298.15 --gamma_ln 1.0 -n 500000 --interval 500 --dt 2.0 \
--restrain-mask '!:WAT&!@H=' -k 4.8 --reference prot_amber.pdb \
--water SPC/E --prev_frame 4000 -p prot_amber.pdb --cuda 1 --npt
fi
