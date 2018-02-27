cmd.load('MyProtein.pdb')
cmd.load('MyBindingSite.pdb')
cmd.load('prot_amber.pdb')
cmd.super("prot_amber", "MyProtein")
cmd.remove("solvent")
cmd.remove("resn Cl- or resn Na\+")
cmd.save("ref.pdb", "prot_amber", 0, "pdb")

cmd.select("bs", "br. MyBindingSite around 3.5 and prot_amber and not (solvent or resn Cl- or resn Na\+) ")
list = []
cmd.iterate("bs and name CA", "list.append(resi)")

res = ''
for i in list: res+=i+","
print res
os.system("echo %s > bs_res.txt" % res)

