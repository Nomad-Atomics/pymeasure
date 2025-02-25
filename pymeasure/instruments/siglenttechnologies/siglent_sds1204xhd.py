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
    
    def set_channel(self, channel, enable=True, coupling="DC",probe="1.00E+01", scale=1.0, offset=0.0):
        """Configures a channel."""
        self.write(f":CHANnel{channel}:SWIT {'ON' if enable else 'OFF'}")
        self.write(f":CHANnel{channel}:COUPling {coupling}")
        self.write(f":CHANnel{channel}:PROBe VAL,{probe}")
        self.write(f":CHANnel{channel}:SCALe {scale}")
        self.write(f":CHANnel{channel}:OFFSet {offset}")
    
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
    
    def capture_screenshot(self, filename="screenshot.bmp"):
        """Captures a screenshot from the Siglent SDS1204X HD oscilloscope and saves it as a BMP file."""

        # ✅ Send command to request BMP image
        self.write("PRIN? BMP")
        time.sleep(1)  # Allow time for scope to process

        # ✅ Read the BMP file header
        header = self.read_bytes(8)  # First 8 bytes contain 'BM' + file size (4 bytes) + reserved (4 bytes)
        #print(f"📸 BMP Header: {header}")

        # ✅ Extract file size from BMP header (bytes 2-6)
        file_size = int.from_bytes(header[2:6], byteorder='little')
        #print(f"📏 Expected BMP file size: {file_size} bytes")

        # ✅ Read the full image data
        raw_data = header + self.read_bytes(file_size - 8)

        # ✅ Save to file
        with open(filename, "wb") as f:
            f.write(raw_data)

        #print(f"✅ Screenshot saved as {filename}")

        return filename

    
    def shutdown(self):
        """Closes connection to the oscilloscope."""
        self.adapter.connection.close()
