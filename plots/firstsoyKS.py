import os
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects
from matplotlib.ticker import IndexLocator, MultipleLocator, FixedLocator
from matplotlib.patches import Rectangle
from core import signatureCollection
from utils import find_files


COLORLIST = ['c', 'orange', 'm', (0.1, 0.7, 0.4), 'r', 'y', 'k']


def flip(items, ncol):
    '''
    This reformats a list of artists or labels to fill rows in legend before columns
    '''
    from itertools import chain
    return list(chain(*[items[i::ncol] for i in range(ncol)]))


def parse_points_ref(reffile):
    collected = []
    recording = False
    tempvals = []
    tempdoys = []

    with open(reffile, 'r') as f:
        for line in f.readlines():
            if recording:
                if line.startswith("\n"):
                    collected.append((tempdoys, tempvals))
                    tempvals = []
                    tempdoys = []
                    recording = False
                else:
                    vals = line.split(" ")
                    tempdoys.append(int(vals[0]))
                    tempvals.append(int(vals[1]))
            elif line.startswith("Point"):
                recording = True

        if recording == True:
            collected.append((tempdoys, tempvals))

    return collected



# import and use ggplot rc style
from mpltools import style
style.use('ggplot')


# create a patheffect object to add a 2pt white casing to lines
pe = [PathEffects.withStroke(linewidth=1.75, foreground="w")]


doyint = 16

extrafilter = "NDVI"

# list of crop names to find within signatures
signaturenames = [#("Soy", "soy_" + extrafilter),
                  #("Corn", "corn_" + extrafilter),
                  ("Sorghum", "sorghum_" + extrafilter),
                  #("Poroto", "poroto"),
                  #("Pasture", "pasture"),
                  #("Forested", "forested"),
                  #("Nothing", "nothing"),
                  #("Other", "other"),
                  #("Wheat", "wheat_" + extrafilter),
                  #("Wheat/Soy Double Crop", "wwheatsoydbl_" + extrafilter),
                 ]
# directory to search for sigs
signaturedirectory = "/Users/phoetrymaster/Documents/School/Geography/Thesis/Data/MODIS_KANSAS_2007-2012/reprojected/Refs/2012clip1test2/clip1/"
oldsigdir = "/Users/phoetrymaster/Documents/School/Geography/Thesis/Data/MODIS_KANSAS_2007-2012/reprojected/Refs/2012/clip1/corn_NDVI_mean.ref"

# dir for output
outputdir = "/Users/phoetrymaster/Documents/School/Geography/Thesis/ThesisTeX/plots/"
#outputdir = "/Users/phoetrymaster/Documents/TeX/deletetest/plots"


# plot name
name = "refinedsorghumKS.pgf"

# find sigs in directory and add to sig collection
meansigs = find_files(signaturedirectory, "mean.ref")


meansignatures = signatureCollection()

for sig in meansigs:
    try:
        meansignatures.add(sig)
    except Exception as e:
        print e

pointsigs = find_files(signaturedirectory, "points.ref")

pointsignatures = signatureCollection()


for sig in pointsigs:
    signame = os.path.splitext(os.path.basename(sig))[0]
    values = parse_points_ref(sig)
    for i, setofvals in enumerate(values):
        try:
            pointsignatures.add_with_values(setofvals[0], setofvals[1], (signame + '_' + str(i)))
        except Exception as e:
            print e


# fonts and other formatting settings
pgf_with_rc_fonts = {"pgf.texsystem": "/usr/texbin/xelatex",
                     'text.color': 'black',
                     "font.family": "serif",
                     "font.serif": ["/Library/Fonts/Baskerville.ttc"],
                     "font.sans-serif": ["Myriad Pro"],
                     'font.size': 10,
                     'font.weight': 'regular',
                     'axes.labelcolor': 'darkgray',
                     'xtick.color': 'darkgray',
                     'ytick.color': 'darkgray',
                     'lines.solid_capstyle': 'round',
                     'lines.solid_joinstyle': 'round',
                     'lines.dash_capstyle': 'round',
                     'lines.dash_joinstyle': 'round',
                     'axes.titlesize': 'small'}

mpl.rcParams.update(pgf_with_rc_fonts)


# create plot
fig, ax1 = plt.subplots(1, figsize=(5.75, 5))


# set otrageous values to be reset with min and max later
mindoy = 10000
maxdoy = -10000
maxlen = 0
DOYlist = []

# plot all the signatures
linestyles= ['-', '--', ':', '-.']


for k, signaturename in enumerate(signaturenames):
    # to track index of sig for crop (i.e. the 1, 2, 3... in Soy_1, Soy_2, Soy_3...)
    # (cannot use i as not all sigs are of the same crop)
    j = 0

    #signaturename = signaturename + "_"  # to refine filtering

    for i, signature in enumerate(pointsignatures.signatures):

        # check to see if signature is of current crop from the crop list (signaturenames); if so create plot
        if signaturename[1].upper() in signature.name.upper():
            #lbl = "Point " + str(j+1)  # create new legend label for signature
            lbl = "Sample Point Signatures"
            vivals = [v/10000.0 for v in signature.vivalues]
            ax1.plot(signature.daysofyear, vivals,
                     color='m', linestyle='-', label=lbl, linewidth=1, alpha=0.40)
            mindoy = min(mindoy, signature.daysofyear[0])  # get lowest doy
            maxdoy = max(maxdoy, signature.daysofyear[-1])  # get highest doy

            if len(signature.daysofyear) > maxlen:
                maxlen = len(signature.daysofyear)
                DOYlist = signature.daysofyear
            j += 1


# k to track index of signature name (i.e. soy is 0, corn is 1...)
for k, signaturename in enumerate(signaturenames):
    # to track index of sig for crop (i.e. the 1, 2, 3... in Soy_1, Soy_2, Soy_3...)
    # (cannot use i as not all sigs are of the same crop)
    j = 0

    #signaturename = signaturename + "_"  # to refine filtering

    for i, signature in enumerate(meansignatures.signatures):

        # check to see if signature is of current crop from the crop list (signaturenames); if so create plot
        if signaturename[1].upper() in signature.name.upper():
            lbl = signaturename[0]# + "_" + str(j+1)  # create new legend label for signature
            color = COLORLIST[k]  # get color from colorlist
            vivals = [v/10000.0 for v in signature.vivalues]
            ax1.plot(signature.daysofyear, vivals,
                     color='m', linestyle=linestyles[j], label="Mean Signature", linewidth=2, path_effects=pe)
            mindoy = min(mindoy, signature.daysofyear[0])  # get lowest doy
            maxdoy = max(maxdoy, signature.daysofyear[-1])  # get highest doy

            if len(signature.daysofyear) > maxlen:
                maxlen = len(signature.daysofyear)
                DOYlist = signature.daysofyear
            j += 1


## set x and y axis tick spacing and min/maxes ##
# create x axis major, minor tick locators starting at 1 and progressing by image interval * 2 and interval
xmajorLocator   = FixedLocator([j for i, j in enumerate(DOYlist) if i % 2 == 0])
xminorLocator   = FixedLocator(DOYlist)

# create y axis major/minor tick locators starting at 0 and progressing by 2000/1000
ymajorLocator   = MultipleLocator(2000/10000.0)
yminorLocator   = MultipleLocator(1000/10000.0)

ax1.set_xlim(mindoy - doyint, maxdoy + doyint)  # add a full imaging interval to set margins on left/right of x axis
ax1.set_ylim(-250/10000.0, 10250/10000.0)  # add 2.5% to min and max to get proper top and bottom margins on y-axis
ax1.xaxis.set_major_locator(xmajorLocator)
ax1.xaxis.set_minor_locator(xminorLocator) #for the minor ticks, use no labels; default NullFormatter
ax1.yaxis.set_major_locator(ymajorLocator)
ax1.yaxis.set_minor_locator(yminorLocator) #for the minor ticks, use no labels; default NullFormatter


# axis labels
ax1.set_xlabel("Day of Year", weight='regular', size=11)
ax1.set_ylabel("NDVI", weight='regular', size=11)


# set number of legend columns and get a list of the artists and labels
ncols = 2
handles, labels = ax1.get_legend_handles_labels()

##finsert invisible rectangle into legend to push sorghum into center column -- not using
#p = Rectangle((0, 0), 0, 0, visible=False)
#handles.insert(6, p)
#labels.insert(6, "")

# flip order to make rows a single signature, not cols
#handles = flip(handles, ncols)
#labels = flip(labels, ncols)

# remove all but one sample point legend item
print(handles, labels)
handles = handles[-2:]
labels = labels[-2:]
print(handles, labels)

# draw legend
legend = ax1.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, -0.125),
                    fancybox=False, shadow=False, ncol=ncols, prop={'size': 9}, frameon=True)

# draw background grid
plt.grid(linewidth=1, which='major')
plt.grid(linewidth=0.5, which='minor')


# draw axis ticks and set color to darkgray
plt.tick_params(axis='both', which='major', direction='out', length=4, width=1, top=False, right=False)
plt.tick_params(axis='both', which='minor', direction='out', length=0)
ax1.xaxis.label.set_color('darkgray')
ax1.yaxis.label.set_color('darkgray')


#save pgf file for plot
plt.savefig(os.path.join(outputdir, name), bbox_extra_artists=(legend,), bbox_inches='tight')


# need to do a find and replace to change all 0.662745 with 0.5
# and all instances of \selectfont with \selectfont\color{textcolor}
#import fileinput

#for line in fileinput.input(os.path.join(outputdir, name), inplace=True):
#    print(line.replace("0.662745", "0.5"))

#for line in fileinput.input(os.path.join(outputdir, name), inplace=True):
#    print(line.replace("\selectfont", "\selectfont\color{textcolor}"))

filedata = "%%Signature of {0} from {1} processed with allsigsKS.py.\n".format(signaturenames, signaturedirectory)

f = open(os.path.join(outputdir, name), 'r')
filedata = filedata + f.read()
f.close()

filedata = filedata.replace("0.662745", "0.5")
filedata = filedata.replace(r"\fontsize{10.000000}{12.000000}\selectfont", r"\fontsize{10.000000}{12.000000}\selectfont\color{textcolor}")

with open(os.path.join(outputdir, name), 'w') as f:
    f.write(filedata)