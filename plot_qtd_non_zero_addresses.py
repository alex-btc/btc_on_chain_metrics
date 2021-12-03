# grafico, depois da base jah baixada:

import matplotlib.pyplot as plt
%matplotlib
import pandas as pd

data_path = 'C:/code/btc_on_chain_metrics/output/'

qty_non_zero_addresses_per_block_df = pd.read_csv(data_path + 'qty_non_zero_addresses_per_block.csv')

qty_non_zero_addresses_per_block_df.iloc[:,1].plot(xlabel='block', ylabel='qty_non_zero_addresses')
#