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
import gtk.gdk
from cv2 import cv
import tarfile
from datetime import datetime

def main( argv = None ):
	filename = datetime.now().strftime( '%Y%m%d%H%M%S.{0}.{1}' )
	tar = tarfile.open( filename.format( 'tar', 'gz' ), 'w:gz' )

	camera = cv.CreateCameraCapture( 0 )
	im = cv.QueryFrame( camera )
	camfile = filename.format( 'camera', 'png' )
	cv.SaveImage( camfile, im )
	tar.add( camfile )
	os.remove( camfile )

	window = gtk.gdk.get_default_root_window()
	size = window.get_size()
	pb = gtk.gdk.Pixbuf( gtk.gdk.COLORSPACE_RGB, False, 8, size[ 0 ], size[ 1 ] )
	pb = pb.get_from_drawable( window, window.get_colormap(), 0, 0, 0, 0, size[ 0 ], size[ 1 ] )
	screenfile = filename.format( 'screen', 'png' )
	pb.save( screenfile, 'png' )
	tar.add( screenfile )
	os.remove( screenfile )

	tar.close()

if __name__ == "__main__":
	sys.exit( main() )
