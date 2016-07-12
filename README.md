# OpsSpace

This repository contains a common toolbox that is used by various operators.
The design goal of this repository is that each set of operators has their own
separate repository where their own tools are 

## Setting Up Workspace

In order to install the operator tools you need, simply run the `install.py` 
script with the list of package names as an argument.
Running `install.py` without any arguments will cause usage information and
a list of valid package names to be displayed.

## Documentation

The documentation is generated using Sphinx to document modules, along with
the sphinxcontrib.programoutput extension to generate scripts' help output.
If these are installed, documentation can be generated with the `Makefile`.
