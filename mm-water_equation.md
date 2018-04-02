```
MM-water = 0.15*water_enthalpy + 0.25*water_entropy \
+ 0.3*( MMGBSA dG Bind(NS) Coulomb + MMGBSA dG Bind(NS) vdW + MMGBSA dG Bind Solv GB )
+ 0.2*( MMGBSA dG Bind(NS) Hbond   + MMGBSA dG Bind(NS) Lipo + MMGBSA dG Bind Packing )
+ 0.1*( Lig Strain Energy )
```





```
            wm_mm_2_eq = """
0.15 * ({1:r_watermap_WaterMap_Enthalpy}) + 
0.25 * ({1:r_watermap_WaterMap_Entropy}) + 
0.30 * (
 ({1:r_psp_Prime_Coulomb} - {4:r_psp_Prime_Coulomb} - {3:r_psp_Prime_Coulomb})+
 ({1:r_psp_Prime_vdW}     - {4:r_psp_Prime_vdW}     - {3:r_psp_Prime_vdW})+
 ({1:r_psp_Prime_Solv_GB} - {2:r_psp_Prime_Solv_GB} - {3:r_psp_Prime_Solv_GB}))+
0.20 * (
 ({1:r_psp_Prime_Hbond}   - {4:r_psp_Prime_Hbond}   - {3:r_psp_Prime_Hbond})+
 ({1:r_psp_Prime_Lipo}    - {4:r_psp_Prime_Lipo}    - {3:r_psp_Prime_Lipo})+
 ({1:r_psp_Prime_Packing} - {2:r_psp_Prime_Packing} - {3:r_psp_Prime_Packing}))+
0.10 * ({4:r_psp_Prime_Energy} - {2:r_psp_Prime_Energy})"""
```
