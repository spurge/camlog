#!/usr/bin/env python
# encoding: utf-8
"""
camlog.py

Takes a snapshot with attached webcam and uploads it to specified url or blog.

Created by spurge on 2012-11-08.
Copyright (c) 2012 Klandestino AB. All rights reserved.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

import os
import sys
import getopt
import gtk.gdk
from cv2 import cv
import tarfile
from datetime import datetime
import urllib2
import re

def pelp():
	print >> sys.stdout, """
Help message ...
"""

def perr( err, expl ):
	print >> sys.stderr, '{2} :: error :: {1} :: {0}'.format(
		err,
		expl,
		datetime.now().strftime( '%Y-%m-%d %H:%M:%S' ),
	)

def plog( verbose, msg ):
	if verbose:
		print >> sys.stdout, '{1} :: debug :: {0}'.format(
			msg,
			datetime.now().strftime( '%Y-%m-%d %H:%M:%S' ),
		)

def main( argv = None ):
	verbose = False
	output = '.'

	if argv is None:
		argv = sys.argv

	try:
		opts, args = getopt.getopt( argv[ 1: ], "hvo:", [ "help", "verbose", "output=" ] )
	except getopt.error, err:
		perr( err, 'Missing arguments' )
		pelp()
		return 2

	for option, value in opts:
		if option in ( "-v", "--verbose" ):
			verbose = True
		if option in ( "-h", "--help" ):
			pelp()
			return 1
		if option in ( "-o", "--output" ):
			output = value

	if not os.path.isdir( output ):
		perr( 'Output error', 'Specified output {0} is not a directory'.format( output ) )
		return 2

	filename = datetime.now().strftime( output + '/%Y%m%d%H%M%S.{0}.{1}' )

	try:
		tar = tarfile.open( filename.format( 'tar', 'gz' ), 'w:gz' )
		plog( verbose, 'Created tar file: {0}'.format( filename.format( 'tar', 'gz' ) ) )
	except IOError, err:
		perr( err, 'Specified output dir {0} is not writeable'.format( output ) )
		return 2

	# Prevent opencv or gtk to do any stderr
	sys.stdout.flush()
	newstdout = os.dup( 2 )
	devnull = os.open( '/dev/null', os.O_WRONLY )
	os.dup2( devnull, 2 )
	os.close( devnull )
	sys.stderr = os.fdopen( newstdout, 'w' )

	camera = cv.CreateCameraCapture( 0 )
	im = cv.QueryFrame( camera )
	camfile = filename.format( 'camera', 'png' )
	cv.SaveImage( camfile, im )
	tar.add( camfile )
	os.remove( camfile )
	plog( verbose, 'Camera snapshot taken: {0}'.format( camfile ) )

	window = gtk.gdk.get_default_root_window()
	size = window.get_size()
	pb = gtk.gdk.Pixbuf( gtk.gdk.COLORSPACE_RGB, False, 8, size[ 0 ], size[ 1 ] )
	pb = pb.get_from_drawable( window, window.get_colormap(), 0, 0, 0, 0, size[ 0 ], size[ 1 ] )
	screenfile = filename.format( 'screen', 'png' )
	pb.save( screenfile, 'png' )
	tar.add( screenfile )
	os.remove( screenfile )
	plog( verbose, 'Screenshot taken: {0}'.format( screenfile ) )

	try:
		locfile = filename.format( 'location', 'txt' )
		locfile_w = open( locfile, 'w' )
	except IOError, err:
		perr( err, 'Could not open location file for writing' )
		return 2

	try:
		ip = re.search( '((?:[0-9]{1,3}\.?){4})', urllib2.urlopen( 'http://checkip.dyndns.org' ).read() ).group( 1 )
		print >> locfile_w, 'IP: {0}'.format( ip )
		plog( verbose, 'Found ip: {0}'.format( ip ) )
	except urllib2.URLError, err:
		perr( err, 'Could not fetch your external ip-address' )
	except AttributeError, err:
		perr( err, 'Could not parse data from check-ip.dyndns.org when fetching your ip-address' )
	
	try:
		html = urllib2.urlopen( 'http://whatismyipaddress.com/ip/{0}'.format( ip ) ).read()
		print >> locfile_w, 'HOSTNAME: {0}'.format( re.search( 'Hostname:<\/th><td>([^<]+)', html ).group( 1 ) )
		print >> locfile_w, 'ISP: {0}'.format( re.search( 'ISP:<\/th><td>([^<]+)', html ).group( 1 ) )
		print >> locfile_w, 'COUNTRY: {0}'.format( re.search( 'Country:<\/th><td>([^<]+)', html ).group( 1 ) )
		print >> locfile_w, 'CITY: {0}'.format( re.search( 'City:<\/th><td>([^<]+)', html ).group( 1 ) )
		print >> locfile_w, 'LATITUDE: {0}'.format( re.search( 'Latitude:<\/th><td>([^<]+)', html ).group( 1 ) )
		print >> locfile_w, 'LONGITUDE: {0}'.format( re.search( 'Longitude:<\/th><td>([^<]+)', html ).group( 1 ) )
		plog( verbose, 'Stuffed your location in: {0}'.format( locfile ) )
	except urllib2.URLError, err:
		perr( err, 'Could not fetch additional location data' )
	except AttributeError, err:
		perr( err, 'Could not parse data from whatismyipaddress.com/ip when fetching your ip-address' )

	locfile_w.close()
	tar.add( locfile )
	os.remove( locfile )
	tar.close()

if __name__ == "__main__":
	sys.exit( main() )
