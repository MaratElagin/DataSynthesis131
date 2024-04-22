from sdv.metadata import SingleTableMetadata
from sdv.single_table import CTGANSynthesizer, GaussianCopulaSynthesizer, CopulaGANSynthesizer, TVAESynthesizer

class Synthesizer:
    def __init__(self, data, epochs=1000):
        self._metadata_obj = SingleTableMetadata()
        self._metadata_obj.detect_from_dataframe(data)
        self.epochs = epochs
        self.data = data 

    @property
    def metadata(self):
        return self._metadata_obj

    @metadata.setter
    def metadata(self, value):
        if isinstance(value, SingleTableMetadata):
            self._metadata_obj = value
        else:
            raise ValueError("Incorrect type for metadata.")

    def ctgan_generate(self, num_rows):
        synthesizer = CTGANSynthesizer(self.metadata, epochs=self.epochs)
        synthesizer.fit(self.data)
        data_generated = synthesizer.sample(num_rows=num_rows)
        
        return data_generated
    
    def gausian_copula_gan_generate(self, num_rows):
        synthesizer = GaussianCopulaSynthesizer(self.metadata)
        synthesizer.fit(self.data)

        data_generated = synthesizer.sample(num_rows=num_rows)

        return data_generated
    
    def copula_gan_generate(self, num_rows):
        synthesizer = CopulaGANSynthesizer(self.metadata)
        synthesizer.fit(self.data)

        data_generated = synthesizer.sample(num_rows=num_rows)

        return data_generated
    
    def tvae_generate(self, num_rows):
        synthesizer = TVAESynthesizer(self.metadata)
        synthesizer.fit(self.data)

        data_generated = synthesizer.sample(num_rows=num_rows)

        return data_generated