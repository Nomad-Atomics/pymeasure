from pymeasure.instruments import Instrument


class SDG2042X(Instrument):
    """
    Driver for the Siglent SDG2042X Arbitrary Waveform Generator.
    
    This supports setting basic waveform parameters, querying status,
    and controlling outputs.
    """
    
    def __init__(self, resourceName, **kwargs):
        super().__init__(
            resourceName,
            "Siglent SDG2042X",
            read_termination="\n",
            write_termination="\n",
            **kwargs
        )

    def reset(self):
        """Reset the instrument."""
        self.write("*RST")
    
    def idn(self):
        """Queries the instrument identification string."""
        return self.ask("*IDN?")
    
    def set_waveform(self, channel, waveform):
        """Set the waveform type on a channel."""
        self.write(f"C{channel}:BSWV WVTP,{waveform}")
    
    def set_frequency(self, channel, frequency):
        """Sets the frequency of the waveform on a channel."""
        self.write(f"C{channel}:BSWV FRQ,{frequency}")
    
    def set_amplitude(self, channel, amplitude):
        """Set the amplitude of the waveform on a channel."""
        self.write(f"C{channel}:BSWV AMP,{amplitude}")
    
    def set_offset(self, channel, offset):
        """Set the DC offset of the waveform on a channel."""
        self.write(f"C{channel}:BSWV OFST,{offset}")
    
    def set_phase(self, channel, phase):
        """Sets the phase of the waveform on a channel."""
        self.write(f"C{channel}:BSWV PHSE,{phase}")
    
    def enable_output(self, channel, state=True):
        """Enable or disable the output for a channel."""
        status = "ON" if state else "OFF"
        self.write(f"C{channel}:OUTP {status}")
    
    def query_waveform_settings(self, channel):
        """Queries waveform settings for a channel."""
        return self.ask(f"C{channel}:BSWV?")
    
    def load_arbitrary_waveform(self, channel, name):
        """Load an arbitrary waveform by name."""
        self.write(f"C{channel}:ARWV NAME,{name}")
    

