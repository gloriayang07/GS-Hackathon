import datetime

from gs_quant.data import Dataset
from gs_quant.session import GsSession, Environment

GsSession.use(Environment.PROD, '77d7c80dec0b44e9868dfaa3a7e2cb36', '4edbc70b2249de3ddc9f303bb373575cb06839fb6857570648fdb772ccf8e377', ('read_product_data',))

ds = Dataset('COVID19_COUNTRY_DAILY_ECDC')
data = ds.get_data()
# print(data)  # peek at first few rows of data
data.reset_index(inplace=True)
data.to_json(r'ecdc.json')
