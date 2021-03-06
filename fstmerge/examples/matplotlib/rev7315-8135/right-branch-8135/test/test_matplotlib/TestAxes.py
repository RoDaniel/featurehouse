"""The Axes unit-test class implementation."""
from mplTest import *
import matplotlib
matplotlib.use( "Agg", warn = False )
import pylab
import numpy as npy
from datetime import datetime
class TestAxes( MplTestCase ):
   """Test the various axes non-plotting methods."""
   tags = [
            'agg',        # uses agg in the backend
            'agg-only',   # uses only agg in the backend
            'PIL',        # uses PIL for image comparison
          ]
   def setUp( self ):
      """Setup any data needed for the unit test."""
      units.register()
   def tearDown( self ):
      """Clean-up any generated files here."""
      pass
   def test_empty_datetime( self ):
      """Test plotting empty axes with dates along one axis."""
      fname = self.outFile( "empty_datetime.png" )
      t0 = datetime(2009, 1, 20)
      tf = datetime(2009, 1, 21)
      fig = pylab.figure()
      pylab.axvspan( t0, tf, facecolor="blue", alpha=0.25 )
      fig.autofmt_xdate()
      fig.savefig( fname )
      self.checkImage( fname )
   def test_formatter_ticker( self ):
      """Test Some formatter and ticker issues."""
      xdata = [ x*units.sec for x in range(10) ]
      ydata1 = [ (1.5*y - 0.5)*units.km for y in range(10) ]
      ydata2 = [ (1.75*y - 1.0)*units.km for y in range(10) ]
      fname = self.outFile( "formatter_ticker_001.png" )
      fig = pylab.figure()
      ax = pylab.subplot( 111 )
      ax.set_xlabel( "x-label 001" )
      fig.savefig( fname )
      self.checkImage( fname )
      fname = self.outFile( "formatter_ticker_002.png" )
      ax.plot( xdata, ydata1, color='blue', xunits="sec" )
      fig.savefig( fname )
      self.checkImage( fname )
      fname = self.outFile( "formatter_ticker_003.png" )
      ax.set_xlabel( "x-label 003" )
      fig.savefig( fname )
      self.checkImage( fname )
      fname = self.outFile( "formatter_ticker_004.png" )
      ax.plot( xdata, ydata2, color='green', xunits="hour" )
      fig.savefig( fname )
      self.checkImage( fname )
      fname = self.outFile( "formatter_ticker_005.png" )
      ax.set_xlabel( "x-label 005" )
      ax.autoscale_view()
      fig.savefig( fname )
      self.checkImage( fname )
