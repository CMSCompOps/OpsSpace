#! /usr/bin/env perl

=pod

=head1 NAME

example.pl -- An example script with documentation

=head1 DESCRIPTION

There is an analyzer class that is used to roughly translate POD
documentation into the .rst format used in Sphinx,
so this comment block will be rendered properly in both
perldoc and sphinx websites.

Besides that, this script does nothing useful.
Go ahead and try it.

=head1 AUTHOR

Daniel Abercrobmie <dabercro@mit.edu>

=cut

use strict;
use warnings;
use 5.010;

say 'This script does nothing useful.';
