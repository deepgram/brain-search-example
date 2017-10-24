"""
Copyright 2017 Deepgram
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
   http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from deepgram import Brain
import argparse, os, time
from glob import glob
FILE_TYPES = '.mp3 .3gp .aifc .mp4 .ogg .aif .wav .amr .flac .wmv .mpg .mkv .mp2 .mov .webm .3gpp .m4a .wma .aiff .aac .3ga'.split()


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-u', '--user', help='API user id', required=True)
  parser.add_argument('-t', '--token', help='API user token', required=True)
  parser.add_argument('-s', '--server', help='URL of the API server to use.')
  parser.add_argument('-r', '--reload', help='Reload all data files to the server.', action='store_true')

  parser.add_argument('query', nargs='+', help='Phrase to search for')
  parser.add_argument('-f', '--file', help='Files to search in.', action='append')
  args = parser.parse_args()

  #Argparse is great, but unfortunately specifying a default will append it to the list so we will check for it
  # explicitly
  fileArgs = args.file
  if len(fileArgs) == 0:
    fileArgs = ['./*']
  files = []
  #Now strip out only the files that have the right file extension
  for file in fileArgs:
    files += [file for file in glob(file) if (os.path.splitext(file)[1].lower() in FILE_TYPES)]

  if len(files) == 0:
    print('No valid input files found.')
    exit(0)

  #print(args.query)
  #print(files)

  if args.server is not None:
    brainAPI = Brain(url=args.server, user_id= args.user_id, token = args.token)
  else:
    brainAPI = Brain(user_id=args.user, token=args.token)

  #To save time, lets look for any previous assets that we have loaded
  previousAssets = {}
  if not args.reload:
    for asset in brainAPI.assets:
      if ('status' not in asset or asset['status'] != 'failed') and asset['transcript_exists'] == True and asset[
        'metadata'] is not None and 'filename' in asset['metadata']:
        previousAssets[asset['metadata']['filename']] = asset['asset_id']

  #now lets load the files into brain or re-use them if they are already there
  assetIds = []
  loadingAssets = set()
  for file in files:
    basename = os.path.basename(file)
    if basename in previousAssets:
      print('Reusing: {}'.format(basename))
      assetIds.append(previousAssets[basename])
    else:
      print('Loading: {}'.format(basename))
      with open(file, mode='rb') as data:
        #We want to make this async so that we can let brain process while we load more assets
        assetId = brainAPI.uploadAsset(data, async=True, metadata={'filename':basename})['asset_id']
        assetIds.append(assetId)
        loadingAssets.add(assetId)

  #Since we loaded asynchronously we need to wait untill all assets have finished loading to search them
  while len(loadingAssets) > 0:
    print('Waiting for assets to process...')
    for assetId in loadingAssets.copy():
      asset = brainAPI.asset(assetId)
      if asset['transcript'] is not None:
        loadingAssets.remove(assetId)
    if len(loadingAssets) > 0:
      #give it a few second until we check again
      time.sleep(2.0)

  #now search!
  results = brainAPI.searchAssets(' '.join(args.query), assetIds)
  print(results)

if __name__ == '__main__':
  main()
