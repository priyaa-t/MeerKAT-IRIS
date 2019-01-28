from __future__ import print_function

import sys
import os
import shutil

import config_parser
from cal_scripts import bookkeeping
from config_parser import validate_args as va
from recipes.almapolhelpers import *

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format="%(asctime)-15s %(levelname)s: %(message)s", level=logging.INFO)

def do_cross_cal_apply(visname, fields, calfiles, caldir):
    """
    Applies the calibration tables generated by cross_cal.py
    to the input MMS.
    """

    base = visname.replace('.ms', '')
    gain1file   = os.path.join(caldir, base+'.g1cal')
    dtempfile   = os.path.join(caldir, base+'.dtempcal')
    xy0ambpfile = os.path.join(caldir, base+'.xyambcal')
    xy0pfile    = os.path.join(caldir, base+'.xycal')
    calfiles = calfiles._replace(xpolfile=xy0pfile)
    fields = fields._replace(xpolfield=fields.dpolfield)


    if len(fields.gainfields) > 1:
        fluxfile = calfiles.fluxfile
    else:
        fluxfile = calfiles.gainfile

    logger.info("applying calibrations: primary calibrator")
    applycal(vis=visname, field = fields.fluxfield,
            selectdata = False, calwt = False, gaintable = [calfiles.kcorrfile,
                calfiles.bpassfile, fluxfile, calfiles.dpolfile,
                calfiles.xdelfile, calfiles.xpolfile],
        gainfield = [fields.kcorrfield,fields.bpassfield, fields.fluxfield,
            fields.dpolfield,fields.xdelfield, fields.xpolfield],
        parang = True)


    #print " applying calibrations: polarization calibrator"
    #applycal(vis=visname, field = fields.dpolfield,
    #        selectdata = False, calwt = True, gaintable = [calfiles.kcorrfile,
    #            calfiles.bpassfile, fluxfile, calfiles.dpolfile,
    #            calfiles.xdelfile, calfiles.xpolfile],
    #    gainfield = [fields.kcorrfield,fields.bpassfield,fields.secondaryfield,
    #        fields.dpolfield,fields.xdelfield,fields.xpolfield],
    #    parang= True)


    logger.info(" applying calibrations: secondary calibrators")
    applycal(vis=visname, field = fields.secondaryfield,
            selectdata = False, calwt = False,
        gaintable = [calfiles.kcorrfile, calfiles.bpassfile, fluxfile,
            calfiles.dpolfile, calfiles.xdelfile, calfiles.xpolfile],
        gainfield = [fields.kcorrfield, fields.bpassfield,
            fields.secondaryfield, fields.dpolfield, fields.xdelfield,
            fields.xpolfield],
        parang= True)

    logger.info(" applying calibrations: target fields")
    applycal(vis=visname, field = fields.targetfield,
            selectdata = False, calwt = False, gaintable = [calfiles.kcorrfile,
                calfiles.bpassfile, fluxfile, calfiles.dpolfile,
                calfiles.xdelfile, calfiles.xpolfile],
        gainfield = [fields.kcorrfield, fields.bpassfield,
            fields.secondaryfield, fields.dpolfield, fields.xdelfield,
            fields.xpolfield],
        parang= True)



if __name__ == '__main__':
    # Get the name of the config file
    args = config_parser.parse_args()

    # Parse config file
    taskvals, config = config_parser.parse_config(args['config'])

    visname = va(taskvals, 'data', 'vis', str)
    visname = os.path.split(visname.replace('.ms', '.mms'))[1]

    calfiles, caldir = bookkeeping.bookkeeping(visname)
    fields = bookkeeping.get_field_ids(taskvals['fields'])

    do_cross_cal_apply(visname, fields, calfiles, caldir)
