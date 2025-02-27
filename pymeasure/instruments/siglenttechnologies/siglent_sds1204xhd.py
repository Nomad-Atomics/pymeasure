import numpy as np
from pymeasure.instruments import Instrument
import time
import struct

class SDS1204XHD(Instrument):
    def __init__(self, resourceName, **kwargs):
        super().__init__(
            resourceName,
            "Siglent SDS1204X HD",
            read_termination="\n",
            write_termination="\n",
            **kwargs
        )
    
    def set_channel(self, channel, enable=True, coupling="DC",probe="1.00E+01", scale=1.0, offset=0.0, impedance = "ONEMeg"):
        """Configures a channel."""
        self.write(f":CHANnel{channel}:SWIT {'ON' if enable else 'OFF'}")
        self.write(f":CHANnel{channel}:COUPling {coupling}")
        self.write(f":CHANnel{channel}:PROBe VAL,{probe}")
        self.write(f":CHANnel{channel}:SCALe {scale}")
        self.write(f":CHANnel{channel}:OFFSet {offset}")
        self.write(f":CHANnel{channel}:IMP {impedance}")
    
    def set_timebase(self, scale):
        """Sets the timebase scale (seconds per division)."""
        self.write(f":TIMebase:SCALe {scale}")
    
    def set_trigger(self, mode="EDGE", source=1, level=0.0, edge="RISE"):
        """Sets the trigger mode, source, level, and edge."""
        self.write(f":TRIGger:MODE {mode}")
        self.write(f":TRIGger:{mode}:SOURce CHAN{source}")
        self.write(f":TRIGger:{mode}:LEVel {level}")
        self.write(f":TRIGger:{mode}:EDGE:SLOPe {edge}")
    
    def stop(self):
        """Stops waveform acquisition."""
        self.write(":STOP")
    
    def run(self):
        """Ensures the oscilloscope resumes normal acquisition properly."""
        self.write(":TRIGger:RUN")  # Start acquisition
        #self.ask("*OPC?")   # Ensure operation is completed before continuing
    
    def capture_screenshot(self, filename="screenshot.png"):
        """
        Captures a screenshot from the scope in PNG format.
        This version checks for the standard PNG file signature and then reads
        all available data.
        """
        self.write("PRINt? PNG")
        time.sleep(1)  # Allow time for the scope to process

        # Read the first 8 bytes, which should be the PNG signature.
        signature = self.read_bytes(8)
        if signature != b'\x89PNG\r\n\x1a\n':
            raise Exception("Unexpected PNG signature: " + str(signature))

        # Now, read the rest of the data.
        # Depending on the VISA adapter, read_bytes(-1) might work to read all remaining data.
        remaining_data = self.read_bytes(-1)
        raw_data = signature + remaining_data

        # Save the data to file.
        with open(filename, "wb") as f:
            f.write(raw_data)

        return filename
    
    def configure_fft_fullscreen(self,channel, max_frequency):
        '''sets function 1 to pull channel data and display as full FFT screen with a given max range
        Returns read back max value of FFT measurement in dBm
        '''
        
        #Hide input waveform
        self.write(":CHANnel1:VISible OFF")
        
        #Turn on function 1
        self.write(f"FUNC1 ON")
        
        #Set FFT function operation
        self.write("FUNC1:OPER FFT")
        
        #Set source
        self.write(f":FUNCtion1:SOURce1 C{channel}")

        # Enable FFT-only display.
        self.write(":FUNCtion:FFTDisplay FULL")

        #Set to average mode
        self.write(":FUNCtion1:FFT:MODE AVERage")

        #Set to dBm
        self.write(":FUNCtion1:FFT:UNIT dBm")

        #Let it average a tad
        time.sleep(0.3)
        
        #Set the disp range
        center_frequency = max_frequency / 2.0
        self.write(f":FUNCtion1:FFT:SPAN {max_frequency}")
        self.write(f":FUNCtion1:FFT:HCEN {center_frequency}")
        
        self.write("MEASure ON")
        self.write(":MEASure:SIMPle:ITEM MAX,ON")
        self.write(":MEASure:SIMPle:SOURce F1")
        
        time.sleep(0.2)
        
        return self.ask("MEAS:SIMP:VAL? MAX")

        
    
    def shutdown(self):
        """Closes connection to the oscilloscope."""
        self.adapter.connection.close()
