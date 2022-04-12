# This Python 3.x file uses the following encoding: utf-8
# Feature-plugin for PyMol 2.x (Windows version) Copyright Notice.
# ====================================================================
#
# The feature-plugin source code is copyrighted, but you can freely
# use and copy it as long as you don't change or remove any of the
# copyright notices.
#
# ----------------------------------------------------------------------
# Dipolemaker plugin is Copyright (C) 2020 by Goetz Parsiegla
#
#                        All Rights Reserved
#
# Permission to use, copy, modify, distribute, and distribute modified
# versions of this software and its documentation for any purpose and
# without fee is hereby granted, provided that the above copyright
# notice appear in all copies and that both the copyright notice and
# this permission notice appear in supporting documentation, and that
# the name of Goetz Parsiegla not be used in advertising or publicity
# pertaining to distribution of the software without specific, written
# prior permission.
#
# GOETZ PARSIEGLA DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
# SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS.  IN NO EVENT SHALL DANIEL SEELIGER BE LIABLE FOR ANY
# SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER
# RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF
# CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
# CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
# ----------------------------------------------------------------------
#
# Calculates Gridpoints and executes FEATURE under cygwin to detect Ca-sites.
# If you find bugs or have any suggestions for future versions contact me:
# goetz.parsiegla@imm.cnrs.fr

import sys
import os

# pymol.Qt is a wrapper which provides the PySide2/Qt5/Qt4 interface
# if it has been installed in python before !
from pymol.Qt import QtWidgets
from pymol import cmd
from glob import glob
import shutil

def __init_plugin__(app=None):
    '''
    Add an entry to the PyMOL "Plugin" menu
    '''
    from pymol.plugins import addmenuitemqt
    addmenuitemqt('Feature', run_plugin_gui)


# global reference to avoid garbage collection of our dialog
dialog = None

def run_plugin_gui():
    global dialog
    if dialog is None:
        dialog = QtWidgets.QDialog() # now global dialog holds a Qtobject

    # filename of our UI file
    uifile = os.path.join(os.path.dirname(__file__), 'form.ui')

    # load the UI file into our dialog
    from pymol.Qt.utils import loadUi
    form = loadUi(uifile, dialog)
    Feature(form) # call the plugin class and pass the form as an argument
    dialog.show()

# --------------- Plugin code starts here --------------------

class Feature:
    def __init__(self, form):
        self.form = form

        # get a temporary file directory
        if not sys.platform.startswith('win'):
            home = os.environ.get('HOME')
        else:
            home = os.environ.get('HOMEPATH')

        tmp_dir = os.path.join(home,'.PyMol_plugin')
        if not os.path.isdir(tmp_dir):
            os.mkdir(tmp_dir)
            print("Created temporary files directory:  %s" % tmp_dir)

        # Assign nonlocal variables to lineEdits and spinBoxes  
        statusline = self.form.lineEdit
        self.dssp_location = self.form.lineEdit_2
        self.R_location = self.form.lineEdit_3
        self.Rscript_location = self.form.lineEdit_5
        self.feature_data_location = self.form.lineEdit_6
        self.pdb_dir_location = self.form.lineEdit_7
        self.models_dir_location = self.form.lineEdit_8
        self.cygwin_location = self.form.lineEdit_4
        set_gridspacing = self.form.doubleSpinBox
        set_gridspacing.setSingleStep(0.1)
        set_precision = self.form.spinBox
        set_precision.setSingleStep(1)

        # defaults
        self.config_settings = {}        
        self.gridspacing = (0.48)
        self.precision = (99)
        prot = ""

        def set_statusline(text):
            statusline.clear()
            statusline.insert(text)

        #-----------------------------------------------------------

        # Config page

        install_text = """
        <html><body>This version of the Feature Plugin is planned to be used under Windows.<br>
        To run Feature, you have to install Cygwin first.<br> It then might be usefull to install a package manager (like apt-cyg, sage or others)
        and install gcc and compile FEATURE 3.1 found at : https://simtk.org/projects/feature in the cygwin environment.<br>
        The necessary R scripts and the model to predict Ca sites can be found at the same adress as feature.<br>
        Finally you further neeed the windows executables of R and dssp.</body></html>
        """

        # Config functions

        def get_dssp_location(self):
            filedialog = QtWidgets.QFileDialog()
            if filedialog.exec_():
                filename = ''.join(
                    map(str, filedialog.selectedFiles()))
                set_dssp_location(filename)
            else:
                None

        def get_R_location(self):
            filedialog = QtWidgets.QFileDialog()
            if filedialog.exec_():
                filename = ''.join(
                    map(str, filedialog.selectedFiles()))
                set_R_location(filename)
            else:
                None

        def get_Rscript_path(self):
            dirdialog = QtWidgets.QFileDialog()
            dirdialog.setFileMode(QtWidgets.QFileDialog.Directory)
            if dirdialog.exec_():
                dirname = ''.join(
                    map(str, dirdialog.selectedFiles()))+'/'
                set_Rscript_path(dirname)
            else:
                None

        def get_feature_data_path(self):
            dirdialog = QtWidgets.QFileDialog()
            dirdialog.setFileMode(QtWidgets.QFileDialog.Directory)
            if dirdialog.exec_():
                dirname = ''.join(
                    map(str, dirdialog.selectedFiles()))+'/'
                set_feature_data_path(dirname)
            else:
                None

        def get_pdb_dir_path(self):
            dirdialog = QtWidgets.QFileDialog()
            dirdialog.setFileMode(QtWidgets.QFileDialog.Directory)
            if dirdialog.exec_():
                dirname = ''.join(
                    map(str, dirdialog.selectedFiles()))+'/'
                set_pdb_dir_path(dirname)
            else:
                None

        def get_models_dir_path(self):
            dirdialog = QtWidgets.QFileDialog()
            dirdialog.setFileMode(QtWidgets.QFileDialog.Directory)
            if dirdialog.exec_():
                dirname = ''.join(
                    map(str, dirdialog.selectedFiles()))+'/'
                set_models_dir_path(dirname)
            else:
                None

        def get_cygwin_path(self):
            dirdialog = QtWidgets.QFileDialog()
            dirdialog.setFileMode(QtWidgets.QFileDialog.Directory)
            if dirdialog.exec_():
                dirname = ''.join(
                    map(str, dirdialog.selectedFiles()))+'/'
                set_cygwin_path(dirname)
            else:
                None

        def set_dssp_location(filename):
            self.dssp_location.clear()
            self.dssp_location.insert(filename)
            self.dssp_exe = filename
            self.config_settings['dssp_exe'] = filename


        def set_R_location(filename):
            self.R_location.clear()
            self.R_location.insert(filename)
            self.R_exe = filename
            self.config_settings['R_exe'] = filename

        def set_Rscript_path(dirname):
            self.Rscript_location.clear()
            self.Rscript_location.insert(dirname)
            self.Rscript_path = dirname
            self.config_settings['Rscript_path'] = dirname

        def set_feature_data_path(dirname):
            self.feature_data_location.clear()
            self.feature_data_location.insert(dirname)
            self.feature_data_path = dirname
            self.config_settings['feature_data_path'] = dirname

        def set_pdb_dir_path(dirname):
            self.pdb_dir_location.clear()
            self.pdb_dir_location.insert(dirname)
            self.pdb_dir_path = dirname
            self.config_settings['pdb_dir_path'] = dirname

        def set_models_dir_path(dirname):
            self.models_dir_location.clear()
            self.models_dir_location.insert(dirname)
            self.models_dir_path = dirname
            self.config_settings['models_dir_path'] = dirname

        def set_cygwin_path(dirname):
            self.cygwin_location.clear()
            self.cygwin_location.insert(dirname)
            self.cygwin_path = dirname
            self.config_settings['cygwin_path'] = dirname

        def read_plugin_config_file():
            config_file_name = os.path.join(tmp_dir,"new_feature_plugin.conf")
            self.config_settings = {}
            self.config_settings['dssp_exe'] = ''
            self.config_settings['R_exe'] = ''
            self.config_settings['Rscript_path'] = ''
            self.config_settings['feature_data_path'] = ''
            self.config_settings['pdb_dir_path'] = ''
            self.config_settings['models_dir_path'] = ''
            self.config_settings['cygwin_path'] = ''
            if os.path.isfile(config_file_name):
                set_statusline('Reading configuration file: %s' % config_file_name)
                lst = fileopen(config_file_name,'r').readlines()
                for line in lst:
                    if line[0]!='#':
                        entr = line.split('=')
                        self.config_settings[entr[0].strip()] = entr[1].strip()
                set_dssp_location(self.config_settings['dssp_exe'])
                set_R_location(self.config_settings['R_exe'])
                set_Rscript_path(self.config_settings['Rscript_path'])
                set_feature_data_path(self.config_settings['feature_data_path'])
                set_pdb_dir_path(self.config_settings['pdb_dir_path'])
                set_models_dir_path(self.config_settings['models_dir_path'])
                set_cygwin_path(self.config_settings['cygwin_path'])
            else:
                set_statusline('Configuration file not found')
            return self.config_settings

        def save_plugin_config_file():
            config_file_name = os.path.join(tmp_dir,"new_feature_plugin.conf")
            fp = fileopen(config_file_name,'w')
            print('#========================================', file=fp)
            print('# Feature Plugin configuration file', file=fp)
            self.config_settings['dssp_exe'] = self.dssp_location.text()
            self.config_settings['R_exe'] = self.R_location.text()
            self.config_settings['Rscript_path'] = self.Rscript_location.text()
            self.config_settings['feature_data_path'] = self.feature_data_location.text()
            self.config_settings['pdb_dir_path'] = self.pdb_dir_location.text()
            self.config_settings['models_dir_path'] = self.models_dir_location.text()
            self.config_settings['cygwin_path'] = self.cygwin_location.text()
            for key, val in self.config_settings.items():
                print(key, '=', val, file=fp)
            fp.close()
            set_statusline('Wrote configuration file %s' % config_file_name)

        def fileopen(filename, mode):
            if mode == 'w' and os.path.isfile(filename):
                p = os.path.abspath(filename)
                b = os.path.basename(p)
                pa, n = p.split(b)
                tmp = '#'+b+'#'
                fn = os.path.join(pa, tmp)
                if os.path.exists(fn):
                    os.remove(fn)
                    os.rename(filename, fn)
                else:
                    os.rename(filename, fn)
                set_statusline('Backing up %s to %s' % (filename, fn))
            try:
                fp = open(filename, mode)
                return fp
            except:
                set_statusline('Error','Could not open file %s' % filename)
                return None

        # Run page buildup
        self.form.textBrowser.setHtml(install_text)
        self.config_settings = read_plugin_config_file()

        #------------------------------------------------------------------

        # Feature page

        intro_text = """
        <html><body>Calculates a block of gridpoints around a .pdb file and
        creates a .pdb file of Ca site predictions with FEATURE and refined
        with R as described by :<br>
        W.Zhou, G.W.Tang and R.B.Altman (2015) J Chem Inf Model,55(8),p1663–1672.<br> 
        1. Open the structure in PyMol<br>
        2. Import and select it in the plugin<br>
        3. Make the grid<br>
        4. Run Feature to create the Microenvironment and score it<br>
          (This runs under cygwin and takes a while ...)<br>
        5. Refine the sites with 'R'<br>
        6. Create the .pdb-file of the sites and visualize them in pyMol</body></html> 
        """

        # Feature functions

        def import_objects():
            self.form.comboBox.clear()
            lst = cmd.get_names("selections")+cmd.get_names()
            if 'sele' in lst:
                lst.remove('sele')
            if 'cgo' in lst:
                lst.remove('cgo')
            lst.insert(0, '')
            object_list = lst
            self.form.comboBox.addItems(object_list)

        def import_models():
            self.form.comboBox_2.clear()
            model_list =[]
            list_raw = glob(os.path.join(self.models_dir_path,"*.model"))
            for item in list_raw:
                model_name = item.split("\\")[-1]
                model_list.append(model_name) 
            self.form.comboBox_2.addItems(model_list)

        def makegrid_object_selected():
            prot = self.form.comboBox.currentText()
            if prot == "":
                set_statusline("No structure selected")
            else:
                set_statusline("Calculating gridpoints ....")
                borders = findborders(prot)
                write_ptf(borders, prot)

        def findborders(selobj):
            xyz=[]
            cmd.iterate_state(1, selobj, 'xyz.append([x,y,z])', space=locals(), atomic=0)
            xlist=[item[0] for item in xyz]
            ylist=[item[1] for item in xyz]
            zlist=[item[2] for item in xyz]
            # extend gridspacing 1 A further than borders
            highx = max(xlist)+1    
            lowx = min(xlist)-1
            highy = max(ylist)+1
            lowy = min(ylist)-1
            highz = max(zlist)+1
            lowz = min(zlist)-1
            borders = [highx,lowx,highy,lowy,highz,lowz]
            print("borders (+/-x,+/-y,+/-z) :", borders)
            print("with spacing :", set_gridspacing.value())
            return borders
        
        def write_ptf(borders, prot):
            filename = prot+".ptf"
            with open(filename, 'w') as outfile:
                xval = borders[1]
                yval = borders[3]
                zval = borders[5]
                while xval <= borders[0]:
                    if xval <= borders[0]:
                        yval=borders[3]
                    while yval <= borders[2]:
                        if yval <= borders[2]:
                            zval=borders[5]
                        while zval <= borders[4]:                      
                            line = prot+" "+'{:8.3f}'.format(xval)+" "+'{:8.3f}'.format(yval)+" "+'{:8.3f}'.format(zval)+"\n" 
                            outfile.write(line)
                            zval = zval+set_gridspacing.value()
                        yval = yval+set_gridspacing.value()
                    xval = xval+set_gridspacing.value()
                set_statusline("Created %s" % filename)

        def posixer (current_path):
            posix_path = current_path.replace("\\", "/")
            return posix_path

        def run_feature(): 
            prot = self.form.comboBox.currentText()
            if prot == "":
                set_statusline("No structure selected")
            else:
                None
            gridfile = (prot+".ptf")
            dsspfile = (prot+".dssp")
            feature_model = self.form.comboBox_2.currentText()
            if ( not os.path.isfile(gridfile)):
                set_statusline('Could not find %s in current directory' % gridfile)
            else:
                if ( not os.path.isfile(dsspfile)):
                    cmd.save(prot+".pdb", prot)
                    command = 'call "%s" -i %s.pdb -o %s ' % (self.dssp_exe, prot, dsspfile)
                    print(command)
                    os.system(command)
                    set_statusline("Created %s" % dsspfile)
                model_path = self.models_dir_path
                model= os.path.join(model_path, feature_model)
                if ( not os.path.isfile(model)):
                    set_statusline('Could not find %s in current directory' % model)
                else:
                    current_path=os.path.abspath(os.curdir)
                    current_posix_path=posixer(current_path)
                    self.pdb_path = self.pdb_dir_path
                    pdb_posix_path = posixer(str(self.pdb_path))
                    feature_data_path = self.feature_data_path
                    feature_posix_path = posixer(str(feature_data_path))
                    model_rel_path=os.path.relpath(model_path)
                    rel_model=os.path.join(model_rel_path,feature_model)
                    rel_model_posix=posixer(str(rel_model))                
                    filename = "featurize.sh"
                    with open(filename, 'w') as outfile:
                        outfile.write('#!/bin/bash \n')
                        outfile.write('pushd %s > /dev/null \n' % current_posix_path)
                        outfile.write('export FEATURE_DIR=%s \n' % feature_posix_path)
                        outfile.write('export DSSP_DIR=%s \n' % current_posix_path)
                        outfile.write('export PDB_DIR=%s \n' % pdb_posix_path)
                        outfile.write('featurize -P %s.ptf > %s_grid.ff \n' % ( prot, prot))
                        outfile.write('scoreit %s %s_grid.ff > %s_grid.hits \n' % (rel_model_posix, prot, prot))
                    bash = (os.path.join(self.cygwin_path,"bin\\bash.exe"))
                    command = 'call %s -li < %s' % (bash, filename)
                    print(command)
                    os.system(command)
                    set_statusline("Created %s_grid.ff and %s_grid.hits ..." % (prot, prot))

        def refine_results():
            prot = self.form.comboBox.currentText()
            if prot == "":
                set_statusline("No structure selected")
            else:
                write_rscript(prot)
                run_rscript(prot)

        def write_rscript(prot):
            if not os.path.isfile("findsites.R"):
                findsites = (os.path.join(self.Rscript_path,"findsites.R"))
                shutil.copy(findsites,os.curdir)
                set_statusline('Copied %s in current directory' % "findsites.R")
            else:
                filename = (prot+".R")
                precision = self.precision
                Rscript_rel_path=os.path.relpath(self.Rscript_path)
                with open(filename, 'w') as outfile:
                    outfile.write('source("findsites.R")\n')
                    outfile.write('dat <- read.table("%s_grid.hits", sep = "\t")\n' % prot)
                    outfile.write('dat <- dat[,2:5]\n')
                    outfile.write('names(dat) <- c("scores", "x", "y", "z")\n')
                    outfile.write('pred <- predictSites(dat, precision = "%s", refine.radius = 3.5)\n' % precision)
                    outfile.write('pred <- matrix(pred, ncol = dim(pred)[2])\n')
                    outfile.write('pred <- cbind(rep("%s", dim(pred)[1]), pred)\n' % prot)
                    outfile.write('write.matrix(pred, file = "%s.pred", sep = " ")\n' % prot)
                set_statusline("Created %s" % filename)

        def run_rscript(prot):       
            rscript = (prot+".R")
            if not os.path.isfile(rscript):
                set_statusline('Could not find %s in current directory' % rscript)
            else:
                command = 'call "%s" --no-restore --no-save < %s' % (self.R_exe, rscript)
                print(command)
                os.system(command)
            set_statusline("Created %s.pred" % prot)

        def make_site_file():
            prot = self.form.comboBox.currentText()
            if prot == "":
                set_statusline("No structure selected")
            else:        
                sites_file = write_site_file(prot)
                cmd.load(sites_file)
                sites = sites_file.split(".")[0]
                cmd.label(sites, "b")
                cmd.show(representation="spheres", selection=sites)
                cmd.spectrum("b", selection=sites)
                cmd.set("sphere_transparency", value=0.6, selection=sites)
            
        def write_site_file(prot):
            predfile = prot+".pred"
            sitefile = prot+"-sites.pdb"
            if os.path.isfile(sitefile):
                os.remove(sitefile)
            if not os.path.isfile(predfile):
                set_statusline('Could not find %s in current directory' % predfile)
            else:
                count = float(1)
                with open(predfile, 'r') as infile:
                    for line in infile:
                        line = line.strip()
                        pred_data = line.split()
                        pdb_x = float(pred_data[1])
                        pdb_y = float(pred_data[2])
                        pdb_z = float(pred_data[3])
                        pdb_score = float(pred_data[10])
                        with open(sitefile, 'a') as outfile: 
                            outline = "ATOM   "+'{:4.0f}'.format(count)+"  CA  CA  X"+'{:4.0f}'.format(count)\
                                        +'{:12.3f}'.format(pdb_x)+'{:8.3f}'.format(pdb_y)+'{:8.3f}'.format(pdb_z)\
                                        +"  1.00"+'{:6.2f}'.format(pdb_score)+"\n"
                            outfile.write(outline)
                        count = count+1
                set_statusline("Created %s" % sitefile)
            return sitefile

        # launch on startup :
        import_objects()
        import_models()

        # Run page buildup
        self.form.textBrowser_2.setHtml(intro_text)
        self.form.comboBox_2.setCurrentText("")        
        self.form.comboBox.setCurrentText("")
        self.form.doubleSpinBox.setValue(self.gridspacing)
        self.form.spinBox.setValue(self.precision)

        # ---------------------------------------------
        # All Button bindings :
        # ---------------------------------------------

        self.form.pushButton.clicked.connect(get_models_dir_path)
        self.form.pushButton_2.clicked.connect(get_pdb_dir_path)
        self.form.pushButton_3.clicked.connect(get_dssp_location)
        self.form.pushButton_4.clicked.connect(get_feature_data_path)
        self.form.pushButton_5.clicked.connect(get_cygwin_path)
        self.form.pushButton_6.clicked.connect(get_Rscript_path)
        self.form.pushButton_7.clicked.connect(get_R_location)
        self.form.pushButton_11.clicked.connect(import_objects)
        self.form.pushButton_10.clicked.connect(makegrid_object_selected)
        self.form.pushButton_9.clicked.connect(run_feature)
        self.form.pushButton_8.clicked.connect(refine_results)
        self.form.pushButton_12.clicked.connect(save_plugin_config_file)
        self.form.pushButton_13.clicked.connect(make_site_file)

        # ----------------------------------------------

