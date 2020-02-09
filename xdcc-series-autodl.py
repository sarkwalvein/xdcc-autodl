import os
import sys
import yaml
import re
import argparse
#from xdcc_dl.xdcc import download_packs
from xdcc_dl.xdcc.XDCCClient import XDCCClient
from xdcc_dl.pack_search import SearchEngines

def get_arg_parser():
    parser = argparse.ArgumentParser(description='XDCC Series Autodownloader')
    parser.add_argument('-v', '--verbose', help='Output additional process details', action='store_true')
    parser.add_argument('-s', '--series', help='YAML file with series configuration')
    return parser
    
def prepare_re_string(search_string):
    search_string = search_string.replace('\\',r'\\' )
    search_string = search_string.replace('|',r'\|')
    search_string = search_string.replace('.',r'\.')
    search_string = search_string.replace('$',r'\$')
    search_string = search_string.replace('^',r'\^')
    search_string = search_string.replace('+',r'\+')
    search_string = search_string.replace('?',r'\?')
    search_string = search_string.replace('(',r'\(')
    search_string = search_string.replace(')',r'\)')
    search_string = search_string.replace('{',r'\{')
    search_string = search_string.replace('}',r'\}')
    search_string = search_string.replace('[',r'\[')
    search_string = search_string.replace(']',r'\]')
    search_string = search_string.replace('*','.*?')
    return search_string

# Determine configuration file path
binary_path = sys.argv[0]
binary_folder = os.path.split(binary_path)[0]

parser = get_arg_parser()
args = parser.parse_args()

if args.series is None:
    config_file_path = os.path.join(binary_folder, "series.yaml")
else:
    config_file_path = args.series
    
if args.verbose is None:
    verbose_flag = False
else:
    verbose_flag = True
    
print("Processing configuration file: " + config_file_path)
print("Verbose output: " + str(verbose_flag))    
    
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
default_episode_limit = config['defaults'].get('episode download limit per execution', 999)

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
        episode_limit = data.get('episode download limit per execution', default_episode_limit)
        episode_download_count = 0
        
        if not os.path.isdir(download_folder):
            print("Creating folder " + download_folder)
            os.mkdir(download_folder)
            
        if 'last episode downloaded' is not in data:
            data[''last episode downloaded'] = 0
            
        while episode_download_count < episode_limit:
            current_search_string_with_wildcard = data['search string'].format(data['last episode downloaded'] + 1)
            current_search_string = current_search_string_with_wildcard.replace('*',' ')
            current_search_string_regex = re.compile(prepare_re_string(current_search_string_with_wildcard), re.IGNORECASE)
            
            if verbose_flag: print("Searching {} for {}: ".format(search_engine_name, current_search_string))
            
            search_results = search_engine.value.search(current_search_string)         
            
            selected_pack = None
            
            if len(search_results) > 0:
                for result in search_results:
                    if verbose_flag: print("Applying {} on {}".format(prepare_re_string(current_search_string_with_wildcard), result.get_filename()))
                    if current_search_string_regex.search(result.get_filename()) is not None:
                        if verbose_flag: print("Match")
                        selected_pack = result
                        if result.get_bot() == preferred_bot:
                            break
                        
                if selected_pack is not None:
                    output_name = ''
                    try:
                        if download_folder != '':
                            selected_pack.set_directory(download_folder)
                            
                        if verbose_flag: print("Downloading {} into {}".format(str(selected_pack), selected_pack.directory))
                            
                        client = XDCCClient(
                            selected_pack,
                            timeout=120,
                            fallback_channel=None,
                            throttle=-1
                        )
                        output_name = client.download()
                    except:
                        print("Process aborted", flush = True)
                        sys.exit()
                    
                    if (output_name == 'Failed' or output_name == ''):
                        print("Download failed: {} from {}".format(selected_pack.get_filename(), selected_pack.get_bot()))
                    else:
                        # Update config file
                        data['last episode downloaded'] += 1
                        file = open(config_file_path, 'w')
                        yaml.dump(config, file)
                        file.close()    
                        episode_download_count += 1
                else:
                    # Last episode available reached
                    break
                
            else:
                # Last episode available reached
                break
    except KeyError:
        print("Error processing series {}: {}".format(series, sys.exc_info()[1]))