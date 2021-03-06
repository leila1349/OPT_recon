#!/usr/bin/env python

#
#  reconall.py
#
#  back projection reconstruction of OPT data
#
#  Leila Baghdadi (adapted from jwalls code)
from sys import argv
from scipy import *
import tempfile, os, sys, optparse
from OPT_recon.libOPT import *
from numpy import *
from pyminc.volumes.factory import *
import string
from time import time, ctime

program_name = 'opt_backproject.py'
def process_options(infile = None, outfile = None , pjFOV= None , 
                       slices = None, offset = None, reconsize = None , 
                       offsetview = None , ROI = None , filt = 'abs_hanning', 
                       plotfile = False , clobber = None, path = None, 
                       flip = True,
                       antialias = 1, window = 5.0 , accuracy = 0.2, offsetfile=None):
 
    #get filename and path separeted 
    infile_path = os.path.dirname(infile)
    if (not infile_path):
       infile_path = makeDir(infile_path)
       infile = infile_path+infile
    print 'inputfile : ', infile
    outfile_path = os.path.dirname(outfile)
    if (not outfile_path):
       if (not path):
          outfile_path = makeDir(outfile_path)
          outfile = outfile_path+outfile
       else:
          path = makeDir(path)
          outfile = path+outfile
    print 'outputfile : ', outfile
    if (offsetfile):
       offsetfile_path = os.path.dirname(offsetfile)
       if (not offsetfile_path):
          offsetfile_path = makeDir(offsetfile_path)
          offsetfile = offsetfile_path + offsetfile
       print 'offsetfile : ', offsetfile 
    else:
       offsetfile = infile
    ## check to make sure all files are ok
    if(not os.path.exists(infile)):
      raise IOError,"The specified input file %s does not exist." % infile

    if(os.path.exists(outfile) and not  clobber):
      raise IOError,"The specified output file %s already exists." % outfile

    if(plotfile and os.path.exists( plotfile) 
       and not  clobber):
      raise IOError,"The specified plot file %s already exists." %  plotfile
  
    ## verifying all the options
    if (pjFOV is None):
      pjFOV = 1.0
    else:
      pjFOV = float( pjFOV)

    inputfile = volumeFromFile(infile,dtype='float')
    if (flip ):
      views, dets, total_slices = inputfile.data.count
    else:
      views, total_slices, dets = inputfile.data.count

    startz,starty,startx=inputfile.starts  
    stepz,stepy,stepx=inputfile.separations
    stepz=stepx
    stepy=stepx
    startz,starty,startx=(0,0,0)

    if (slices is None):
      start_slice = 0
      end_slice = total_slices
    else:
      start_slice = int( slices.split(',')[0])
      end_slice = int( slices.split(',')[1])
      if(end_slice <= start_slice or end_slice > slices):
        raise IOError,"projections are incorrectly formatted"
    
    slices_to_build=end_slice-start_slice
    # figure out which file to use when calculating offset
    if (offsetfile is not None):
       file_to_use = volumeFromFile(offsetfile,dtype='float')
    else:
       file_to_use = inputfile

    if (offset is None):
      offset = 0.0
    elif( offset == "auto"):
      offset_guess = get_coarse_offset(file_to_use, flip)
      #print 'offset_guess',offset_guess
      offset = get_fine_offset(file_to_use,int((end_slice-start_slice)/2+start_slice),float( accuracy),
           start_offset=offset_guess-float( window)/2.0,
           end_offset=offset_guess+float( window)/2.0,
           plotfile= plotfile, flip=flip)
    elif( offset == "twostep"):
      offset_guess = get_coarse_offset(file_to_use, flip)
      x1 = offset_guess-float( window)/2.0
      x2 = offset_guess+float( window)/2.0
      offset_guess2 = get_fine_offset(file_to_use,
                  int((end_slice-start_slice)/2+start_slice),1.0,
                  start_offset=x1,end_offset=x2,
                  plotfile= plotfile, flip=flip)
      offset = get_fine_offset(file_to_use,
           int((end_slice-start_slice)/2+start_slice),float( accuracy),
           start_offset=offset_guess2-2.0, end_offset=offset_guess2+2.0,
           plotfile= plotfile, flip=flip)
    else:
      offset = float( offset )

    print "***** Reconstructing with offset %2.2f  *****" % offset

    if (offsetview is None):
      offsetview = 0
    else:
      offsetview = int( offsetview)

    if (reconsize is None):
      if views < dets:
         r0=dets
         r1=dets
      else:
         r0=views
         r1=views
    else:
      reconsize =  reconsize.split(',')
      if(len(reconsize) != 2):
        raise IOError,"The reconsize is incorrectly formatted."
      r0= int(reconsize[0])
      r1= int(reconsize[1])
    reconsize =[]
    reconsize.append(r0)
    reconsize.append(r1)
    #print reconsize
    if (ROI is None): 
      ROI = ""
    else:
      ROI =  ROI.split(',')
      if(len(ROI) != 4):
        raise IOError,"Incorrectly formatted ROI"
        sx = float(ROI[0])
        ex = float(ROI[1])
        sy = float(ROI[2])
        ey = float(ROI[3])
        if(sx > ey or sy > ey):
          raise IOError,"Incorrectly ordered ROI"
    
    if (not filt in valid_recon_filters):
      raise IOError,"Filter %s is not a valid filter" %  filt
    
    
    antialias = int(antialias)
    
   
    
    print "Minc dimensions are", views, slices_to_build, dets
	
    outputfile=volumeFromDescription(outfile, ("zspace","yspace","xspace"),
                                 (slices_to_build, reconsize[1],reconsize[0]),
                                 (startz,starty,startx), (stepz,stepy,stepx), 
                                 volumeType='float')
    outputfile.copyAttributes(inputfile,'/OPT')
    j=0
    for i in range(start_slice, end_slice): 
      print 'processing projections', i
      if (flip):
        t = inputfile.getHyperslab((0,0,j),(views,dets,1))
      else:
        t = inputfile.getHyperslab((0,j,0),(views,1,dets))
          
      t.shape =(views,dets)
      inslice = t
      outslice = reconstruct(inslice, views, slices_to_build, dets, 
                             offset, reconsize, 
                             pjFOV, ROI, offsetview, antialias,  filt)
      #print 'outslice', outslice.shape[0], outslice.shape[1]
      #creating n-dimensional array to write
      w = ndarray(shape=outslice.shape, dtype=float)
      for p in range(outslice.shape[0]):
        for q in range(outslice.shape[1]):
          w[p][q] = outslice[p][q]
          # Hmm this was having problems on a few machines, investigate!
          #w[:,:] = outslice[:,:]
      outputfile.setHyperslab(w, (j,0,0),(1,outslice.shape[0] ,outslice.shape[1]))
      j+=1

    history1= inputfile.getHistory(size=2048)
    history2= ctime(time()) + string.join(argv)
    history= history1.value+history2+ " Filtered Back projection reconstruction using CTSIM with python wrapper with "+str(offset)+ " unit of pixels correction applied. \n"

    outputfile.addHistory(len(history),history)

    outputfile.writeFile()
    outputfile.closeVolume()
    inputfile.closeVolume()

if __name__ == '__main__':

    usage = "Usage: "+program_name+" [options] input.mnc output.mnc\n"+\
            "   or  "+program_name+" --help";
    description =" Back projection reconstruction code using the CTSim open source software and python boost wrapper to submit and recieve the projections."
    parser=optparse.OptionParser(usage=usage, description=description)
    parser.add_option("-l","--flip", dest="flip", default=True,
                                  action="store_false", help="reconstruct Z,X slices instead of Z,Y")
    parser.add_option("-F","--pjFOV",dest="pjFOV",
				  help="The FOV of the projections")
    parser.add_option("-O","--offsetfile", action="store", type="string", dest="offsetfile",
                                  default=0, 
                                  help="Use given file to calculate offset which will be applied to image.")
    parser.add_option("-o","--offset",dest="offset",
				  help="The offset of the rotational axis from the center of the detectors (in units of pixels).  Use auto for automatic offset determination.  Use twostep for the hopefully optimized auto offset calculation.")
    parser.add_option("-r","--reconsize",dest="reconsize",
				  help="The reconstructed image size nx,ny")
    parser.add_option("-R","--ROI",dest="ROI",
				  help="The region of interest to reconstruct.  Format:  sx,ex,sy,ey")
    parser.add_option("-q","--quiet",dest="verbose",default=True,
				  action="store_false",help="Don't echo the command")
    parser.add_option("-c","--clobber",dest="clobber",
			      action="store_true",help="Overwrite the destination file")
    parser.add_option("-v","--offsetview",dest="offsetview",
				  help="The number of views to offset the gantry")
    parser.add_option("-s","--slices",dest="slices",
				  help="The range of slices (start:end) to reconstruct")
    parser.add_option("-a","--antialias",dest="antialias",default="1",
				  help="antialiasing factor along views dimension")
    parser.add_option("-I","--filter",dest="filt",default="abs_hanning",
                  help="the filter to use with pjrec (e.g. abs_hanning).  see pjrec -h for valid filters")
    parser.add_option("-f", "--plotfile",dest="plotfile",default=False,
                  help="the file that will contain the offset calc plot")
    parser.add_option("-w","--window",dest="window",default="5.0",
                  help="The window across which to calculate various offsets.  This window is centered on the initial guess.")
    parser.add_option("-A","--accuracy",dest="accuracy",default="0.2",
                  help="the accuracy with which to find the correct rotational axis")
    parser.add_option("-p","--path", action="store", type="string",                                                    dest="path",
	          default=0, help="create image using the specified path")

    (options, args) = parser.parse_args()

    if(len(args) < 2):
      parser.error("Abort! Incorrect number of arguments")

    infile, outfile = args
    
    process_options(infile, outfile, options.pjFOV, options.slices, options.offset, options.reconsize, options.offsetview,options.ROI, options.filt, options.plotfile, options.clobber, options.path, options.flip, options.antialias, options.window, options.accuracy, options.offsetfile)
