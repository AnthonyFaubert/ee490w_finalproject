#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Top Block
# Generated: Wed May 27 22:37:18 2020
##################################################

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print "Warning: failed to XInitThreads()"

from PyQt4 import Qt
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import qtgui
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import osmosdr
import sip
import sys
import time


class top_block(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Top Block")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Top Block")
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "top_block")
        self.restoreGeometry(self.settings.value("geometry").toByteArray())

        ##################################################
        # Variables
        ##################################################
        self.samp_rate_AM = samp_rate_AM = int(64e3)
        self.samp_rate = samp_rate = int(1.024e6)
        self.samp_rate_ratio = samp_rate_ratio = int(samp_rate / samp_rate_AM)

        ##################################################
        # Blocks
        ##################################################
        self.rtlsdr_source_0 = osmosdr.source( args="numchan=" + str(1) + " " + "" )
        self.rtlsdr_source_0.set_sample_rate(samp_rate)
        self.rtlsdr_source_0.set_center_freq(433.92e6, 0)
        self.rtlsdr_source_0.set_freq_corr(0, 0)
        self.rtlsdr_source_0.set_dc_offset_mode(0, 0)
        self.rtlsdr_source_0.set_iq_balance_mode(0, 0)
        self.rtlsdr_source_0.set_gain_mode(False, 0)
        self.rtlsdr_source_0.set_gain(10, 0)
        self.rtlsdr_source_0.set_if_gain(20, 0)
        self.rtlsdr_source_0.set_bb_gain(20, 0)
        self.rtlsdr_source_0.set_antenna("", 0)
        self.rtlsdr_source_0.set_bandwidth(1.74e6, 0)
          
        self.qtgui_waterfall_sink_x_0 = qtgui.waterfall_sink_c(
        	1024, #size
        	firdes.WIN_BLACKMAN_hARRIS, #wintype
        	433.92e6, #fc
        	samp_rate, #bw
        	"Raw", #name
                1 #number of inputs
        )
        self.qtgui_waterfall_sink_x_0.set_update_time(0.10)
        self.qtgui_waterfall_sink_x_0.enable_grid(False)
        
        if not True:
          self.qtgui_waterfall_sink_x_0.disable_legend()
        
        if "complex" == "float" or "complex" == "msg_float":
          self.qtgui_waterfall_sink_x_0.set_plot_pos_half(not True)
        
        labels = ["", "", "", "", "",
                  "", "", "", "", ""]
        colors = [0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]
        for i in xrange(1):
            if len(labels[i]) == 0:
                self.qtgui_waterfall_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_waterfall_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_waterfall_sink_x_0.set_color_map(i, colors[i])
            self.qtgui_waterfall_sink_x_0.set_line_alpha(i, alphas[i])
        
        self.qtgui_waterfall_sink_x_0.set_intensity_range(-140, 10)
        
        self._qtgui_waterfall_sink_x_0_win = sip.wrapinstance(self.qtgui_waterfall_sink_x_0.pyqwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_waterfall_sink_x_0_win)
        self.qtgui_time_sink_x_3_0_0 = qtgui.time_sink_f(
        	1024, #size
        	samp_rate_AM, #samp_rate
        	"power", #name
        	1 #number of inputs
        )
        self.qtgui_time_sink_x_3_0_0.set_update_time(0.10)
        self.qtgui_time_sink_x_3_0_0.set_y_axis(-0.01, 2)
        
        self.qtgui_time_sink_x_3_0_0.set_y_label("Amplitude", "")
        
        self.qtgui_time_sink_x_3_0_0.enable_tags(-1, True)
        self.qtgui_time_sink_x_3_0_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0, 0, 0, "")
        self.qtgui_time_sink_x_3_0_0.enable_autoscale(False)
        self.qtgui_time_sink_x_3_0_0.enable_grid(False)
        self.qtgui_time_sink_x_3_0_0.enable_control_panel(False)
        
        if not True:
          self.qtgui_time_sink_x_3_0_0.disable_legend()
        
        labels = ["", "", "", "", "",
                  "", "", "", "", ""]
        widths = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
                  "magenta", "yellow", "dark red", "dark green", "blue"]
        styles = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
                   -1, -1, -1, -1, -1]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]
        
        for i in xrange(1):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_3_0_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_3_0_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_3_0_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_3_0_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_3_0_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_3_0_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_3_0_0.set_line_alpha(i, alphas[i])
        
        self._qtgui_time_sink_x_3_0_0_win = sip.wrapinstance(self.qtgui_time_sink_x_3_0_0.pyqwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_3_0_0_win)
        self.blocks_multiply_conjugate_cc_0 = blocks.multiply_conjugate_cc(1)
        self.blocks_moving_average_xx_0_0 = blocks.moving_average_ff(samp_rate_ratio, 1.0 / samp_rate_ratio, 4 * samp_rate_ratio)
        self.blocks_keep_one_in_n_0_0_0 = blocks.keep_one_in_n(gr.sizeof_float*1, samp_rate_ratio)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_float*1, "/tmp/data.bin", False)
        self.blocks_file_sink_0.set_unbuffered(False)
        self.blocks_complex_to_real_0 = blocks.complex_to_real(1)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_complex_to_real_0, 0), (self.blocks_moving_average_xx_0_0, 0))    
        self.connect((self.blocks_keep_one_in_n_0_0_0, 0), (self.blocks_file_sink_0, 0))    
        self.connect((self.blocks_keep_one_in_n_0_0_0, 0), (self.qtgui_time_sink_x_3_0_0, 0))    
        self.connect((self.blocks_moving_average_xx_0_0, 0), (self.blocks_keep_one_in_n_0_0_0, 0))    
        self.connect((self.blocks_multiply_conjugate_cc_0, 0), (self.blocks_complex_to_real_0, 0))    
        self.connect((self.rtlsdr_source_0, 0), (self.blocks_multiply_conjugate_cc_0, 0))    
        self.connect((self.rtlsdr_source_0, 0), (self.blocks_multiply_conjugate_cc_0, 1))    
        self.connect((self.rtlsdr_source_0, 0), (self.qtgui_waterfall_sink_x_0, 0))    

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "top_block")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()


    def get_samp_rate_AM(self):
        return self.samp_rate_AM

    def set_samp_rate_AM(self, samp_rate_AM):
        self.samp_rate_AM = samp_rate_AM
        self.set_samp_rate_ratio(int(self.samp_rate / self.samp_rate_AM))
        self.qtgui_time_sink_x_3_0_0.set_samp_rate(self.samp_rate_AM)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_samp_rate_ratio(int(self.samp_rate / self.samp_rate_AM))
        self.qtgui_waterfall_sink_x_0.set_frequency_range(433.92e6, self.samp_rate)
        self.rtlsdr_source_0.set_sample_rate(self.samp_rate)

    def get_samp_rate_ratio(self):
        return self.samp_rate_ratio

    def set_samp_rate_ratio(self, samp_rate_ratio):
        self.samp_rate_ratio = samp_rate_ratio
        self.blocks_moving_average_xx_0_0.set_length_and_scale(self.samp_rate_ratio, 1.0 / self.samp_rate_ratio)
        self.blocks_keep_one_in_n_0_0_0.set_n(self.samp_rate_ratio)


def main(top_block_cls=top_block, options=None):

    from distutils.version import StrictVersion
    if StrictVersion(Qt.qVersion()) >= StrictVersion("4.5.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()
    tb.start()
    tb.show()

    def quitting():
        tb.stop()
        tb.wait()
    qapp.connect(qapp, Qt.SIGNAL("aboutToQuit()"), quitting)
    qapp.exec_()


if __name__ == '__main__':
    main()
