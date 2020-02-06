import os
import sys
import yaml
#from xdcc_dl.xdcc import download_packs
from xdcc_dl.xdcc.XDCCClient import XDCCClient
from xdcc_dl.pack_search import SearchEngines

# Determine configuration file path
binary_path = sys.argv[0]
binary_folder = os.path.split(binary_path)[0]

print(binary_path)

if len(sys.argv) > 2:
    config_file_path = sys.argv[1]
else:
    config_file_path = os.path.join(binary_folder, "series.yaml")
    
# Parse configuration file
file = open(config_file_path, 'r')
config = yaml.load(file, Loader=yaml.SafeLoader)
file.close()

if not 'series' in config:
    old_config = config
    # Upgrade to new config style
    config = {'series':old_config,
              'defaults': {
                'preferred bot': '',
                'search engine': 'horriblesubs',
                'download folder': '',
                } }
    # Save updated config
    file = open(config_file_path, 'w')
    yaml.dump(config, file)
    file.close()

# Get defaults
default_preferred_bot = config['defaults']['preferred bot']
default_download_folder = config['defaults']['download folder']
default_search_engine = config['defaults']['search engine']

# Process each entry
series_dict = config['series']
for series in series_dict.keys():
    if series.startswith('skip-'):
        # Skip this series
        continue
        
    data = series_dict[series]
    
    try:
        print("Processing {}...".format(series))
        
        search_string = data['search string']
        
        search_engine_name = data.get('search engine', default_search_engine)
        
        if search_engine_name.lower() == 'nibl':
            search_engine = SearchEngines.NIBL
        elif search_engine_name.lower() == 'ixirc':
            search_engine = SearchEngines.IXIRC
        elif search_engine_name.lower() == 'horriblesubs':
            search_engine = SearchEngines.HORRIBLESUBS
        else:
            print("Unrecognized search engine: {} - using horriblesubs".format(search_engine_name))
            search_engine = SearchEngines.HORRIBLESUBS
            
        preferred_bot = data.get('preferred bot',default_preferred_bot)
        download_folder = data.get('download folder', default_download_folder)
            
        while True:
            search_results = search_engine.value.search(data['search string'].format(data['last episode downloaded'] + 1))         
            
            if len(search_results) > 0:
                selected_pack = search_results[0]
                for result in search_results:
                    if result.get_bot() == preferred_bot:
                        selected_pack = result
                        break
                        
                output_name = ''
                try:
                    if download_folder != '':
                        result.set_directory(download_folder)
                        
                    client = XDCCClient(
                        result,
                        timeout=120,
                        fallback_channel=None,
                        throttle=-1
                    )
                    output_name = client.download()
                except:
                    print("Process aborted", flush = True)
                    sys.exit()
                    #print("Error {} downloading: {} from {}".format(sys.exc_info()[0], result.get_filename(), result.get_bot()))
                
                if (output_name == 'Failed' or output_name == ''):
                    print("Download failed: {} from {}".format(result.get_filename(), result.get_bot()))
                else:
                    # Update config file
                    data['last episode downloaded'] += 1
                    file = open(config_file_path, 'w')
                    yaml.dump(config, file)
                    file.close()                
                
            else:
                # Last episode available reached
                break
    except KeyError:
        print("Error processing series {}: {}".format(series, sys.exc_info()[1]))