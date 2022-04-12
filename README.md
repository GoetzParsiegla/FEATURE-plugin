# FEATURE-Plugin

![image](https://user-images.githubusercontent.com/102952395/161944745-b986e752-e4c6-490f-965a-59ed1f71a183.png)
# How to install ?

Ther are two plugins, one to run with a cygwin compilation of FEATURE, the other with its compilation in a wsl2 (ubuntu) environment. For the second version install the wsl2 environnement according to the well documented procedure : https://docs.microsoft.com/fr-fr/windows/wsl/install

Hints:

You have to execute the command line interface in the admin mode, else the error "the requested operation requires elevation" appears.
You can directly choose which linux distribution to install. I took :> wsl -- install -d Ubuntu-18.04

D'ont forget to change the subsystem from wsl to wsl2 : >wsl --set-default-version 2

If you use an open source version of PyMol from Christophe Gohlkes site, you have to installe Python (3.8 and 3.9 will work fine) and PySide2 (https://pypi.org/project/PySide2/) under Windows according to your Python version. I installed the shiboken2-5.12.2 and PySide2-5.12.2 .whl files for my Python version manually with pip. 
You also need to install 'R' for windows that you find at :

